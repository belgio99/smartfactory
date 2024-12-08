from typing import List, Dict, Any, Tuple
import numpy as np
import json
from rapidfuzz import process, fuzz
import nltk
from nltk.tokenize import sent_tokenize

# Ensure the NLTK 'punkt' tokenizer is available. This is required for sentence tokenization.
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Define the main class RagExplainer to handle attribution of responses to provided context.
class RagExplainer:
    """
    A class for attributing segments of LLM responses to their respective contexts using similarity metrics.
    
    Attributes:
        threshold (float): The minimum similarity score to consider a match valid.
        verbose (bool): If True, detailed output is printed for debugging purposes.
        tokenize_context (bool): If True, context strings are tokenized into sentences.
        use_embeddings (bool): If True, embeddings are used for similarity matching; otherwise, fuzzy matching is used.
        context_sentences (List[str]): A list of all unique sentences extracted from the provided context.
        sentence_info (Dict[str, Dict]): A dictionary mapping each sentence to its source and original context.
        context_embeddings (np.ndarray or None): Precomputed embeddings of context sentences for faster similarity computation.
        embedding_model (SentenceTransformer or None): The model used to generate embeddings.
    """

    def __init__(
        self,
        context: List[Tuple[str, str]] = [],
        threshold: float = 50.0,
        verbose: bool = False,
        tokenize_context: bool = True,
        use_embeddings: bool = True
    ):
        """
        Initializes a RagExplainer object with configurable parameters.

        Args:
            context (List[Tuple[str, str]]): A list of tuples containing (source name, context string).
            threshold (float): The similarity threshold, ranging from 0 to 100.
            verbose (bool): Flag to enable verbose debugging output.
            tokenize_context (bool): If True, splits context into sentences for finer-grained matching.
            use_embeddings (bool): If True, embeddings are used for matching responses to context.
        """
        # Save parameters to the class instance
        self.threshold = threshold
        self.verbose = verbose
        self.tokenize_context = tokenize_context
        self.use_embeddings = use_embeddings
        
        # Initialize storage for context-related data
        self.context_sentences = []  # Stores unique context sentences
        self.sentence_info = {}  # Maps sentences to metadata (source name and original context)
        self.context_embeddings = None  # Stores sentence embeddings if embeddings are used
        
        # Load the embedding model only if embedding-based matching is enabled
        if self.use_embeddings:
            self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        else:
            self.embedding_model = None
        
        # Add the initial context to the class instance, if provided
        self.add_to_context(context)

    def _print_verbose(self, result, textResponse, textExplanation):
        """
        Prints detailed debugging information for a single response segment.
        
        Args:
            result (Dict[str, Any]): Contains the attribution details for the response segment.
            textResponse (str): The response text with references added.
            textExplanation (str): JSON-formatted references explaining the attributions.
        """
        # Print detailed information about the attribution results
        print(f"Response Segment: {result['response_segment']}")
        if result['context']:
            print(f"Attributed Context: {result['context']}")
            print(f"Source Name: {result['source_name']}")
            print(f"Original Context: {result['original_context']}")
            print(f"Similarity Score: {result['similarity_score']:.2f}%")
        else:
            print("No context meets the similarity threshold.")
            print(f"Highest Similarity Score: {result['similarity_score']:.2f}%")
        # Print references and explanations for the overall response
        print("-" * 50)
        print("\nText Response:")
        print(textResponse)
        print("\nText Explanation (JSON):")
        print(textExplanation)
        print("-" * 50)

    def _validate_context(self, context: List[Tuple[str, str]]):
        """
        Validates that the input context is in the expected format.

        Args:
            context (List[Tuple[str, str]]): The context to validate.

        Raises:
            ValueError: If the context is not a list of tuples or if any tuple does not contain valid strings.
        """
        # Ensure the input is a list of tuples
        if not isinstance(context, list):
            raise ValueError(f"The 'context' parameter must be a list of tuples. Received type {type(context).__name__}.")
        # Check that each tuple in the list contains a source name (str) and context (str)
        for i, item in enumerate(context):
            if not (isinstance(item, tuple) and len(item) == 2):
                raise ValueError(f"All items in the 'context' list must be tuples of (source_name, context_string). Item at index {i} is invalid.")
            source_name, ctx = item
            if not isinstance(source_name, str):
                raise ValueError(f"The source name at index {i} must be a string. Received type {type(source_name).__name__}.")
            if not isinstance(ctx, str):
                raise ValueError(f"The context string at index {i} must be a string. Received type {type(ctx).__name__}.")

    def _validate_parameters(self):
        """
        Validates class parameters to ensure they meet constraints.

        Raises:
            ValueError: If any parameter is outside its allowed range or of an incorrect type.
        """
        # Ensure the threshold is a number within the range [0, 100]
        if not isinstance(self.threshold, (int, float)) or not (0 <= self.threshold <= 100):
            raise ValueError(f"The 'threshold' parameter must be a number between 0 and 100. Received {self.threshold}.")
        # Ensure the verbose flag is a boolean
        if not isinstance(self.verbose, bool):
            raise ValueError(f"The 'verbose' parameter must be a boolean. Received type {type(self.verbose).__name__}.")

    def _insert_reference(self, response_segment: str, ref_num: int) -> str:
        """
        Appends a reference number to a response segment.

        Args:
            response_segment (str): The response segment to modify.
            ref_num (int): The reference number to insert.

        Returns:
            str: The response segment with the reference number appended.
        """
        # Append the reference number before punctuation, if present, otherwise at the end
        if response_segment.endswith(('.', ',')):
            return response_segment[:-1] + f'[{ref_num}]' + response_segment[-1]
        else:
            return response_segment + f'[{ref_num}]'

    def _parse_json_context(self, ctx: str) -> List[str]:
        """
        Parses a JSON-formatted context string into a list of key-value formatted sentences.

        Args:
            ctx (str): The input string containing JSON data.

        Returns:
            List[str]: A list of sentences extracted and formatted from the JSON data. Each sentence represents
            a key-value pair or an object in a structured format.

        Raises:
            json.JSONDecodeError: If the input string is not a valid JSON object or array.
        """
        try:
            # Attempt to decode the JSON string into a Python object
            data = json.loads(ctx)
        except json.JSONDecodeError:
            # If the input is not valid JSON, return an empty list
            return []

        # Helper function to format a dictionary as a readable key-value string
        def format_object(obj: dict) -> str:
            """
            Converts a dictionary into a string representation with each key-value pair on a new line.

            Args:
                obj (dict): A dictionary object to format.

            Returns:
                str: A string representation of the dictionary.
            """
            # Initialize a list to store formatted lines
            lines = []
            # Loop through each key-value pair in the dictionary
            for k, v in obj.items():
                # Append the formatted string for each pair
                lines.append(f'"{k}": "{v}"')
            # Join the lines and return as a single string
            return "\n   " + "\n   ".join(lines)

        # Handle cases where the JSON data is a list
        if isinstance(data, list):
            sentences = []  # Initialize a list to hold the formatted strings
            for item in data:
                if isinstance(item, dict):  # Check if the list item is a dictionary
                    formatted = format_object(item)  # Format the dictionary
                    # Only include the formatted string if it is sufficiently long
                    if len(formatted.strip()) >= 10:
                        sentences.append(formatted)
                else:
                    # If the item is not a dictionary, treat it as a plain string
                    if len(str(item).strip()) >= 10:
                        sentences.append(str(item))
            return sentences  # Return the list of formatted sentences

        # Handle cases where the JSON data is a dictionary
        elif isinstance(data, dict):
            formatted = format_object(data)  # Format the dictionary
            # Return the formatted dictionary as a list if it's sufficiently long
            if len(formatted.strip()) >= 10:
                return [formatted]
            else:
                return []

        # If the JSON data is neither a list nor a dictionary, return an empty list
        else:
            return []

    def _process_context(self, context: List[Tuple[str, str]]):
        """
        Processes and tokenizes the context for internal storage.

        Args:
            context (List[Tuple[str, str]]): The input context to process.

        Raises:
            ValueError: If the processed context is empty.
        """
        # List to track newly added context sentences
        new_context_sentences = []

        for idx, (source_name, ctx) in enumerate(context):
            # Attempt to parse JSON-formatted context
            json_sentences = self._parse_json_context(ctx)

            # Decide whether to use JSON-parsed sentences or tokenize plain text
            ctx_strings = json_sentences if json_sentences else (
                sent_tokenize(ctx) if self.tokenize_context else [ctx]
            )

            # Ensure the context is not empty after processing
            if not ctx_strings:
                raise ValueError(f"The context at index {idx} is empty after tokenization or JSON parsing.")

            # Add each unique sentence to the internal storage
            for string in ctx_strings:
                if len(string.strip()) >= 10 and string not in self.sentence_info:
                    self.context_sentences.append(string)
                    self.sentence_info[string] = {'source_name': source_name, 'original_context': ctx}
                    new_context_sentences.append(string)

        # Generate embeddings for new sentences if embeddings are enabled
        if self.use_embeddings and new_context_sentences:
            new_embeddings = self.embedding_model.encode(new_context_sentences, convert_to_tensor=True)
            # Concatenate new embeddings with existing ones
            self.context_embeddings = (
                np.concatenate((self.context_embeddings, new_embeddings.cpu()), axis=0)
                if self.context_embeddings is not None
                else new_embeddings.cpu()
            )

    def add_to_context(self, extra_context: List[Tuple[str, str]]):
        """
        Adds new context to the existing stored context.

        Args:
            extra_context (List[Tuple[str, str]]): Additional context to be added.

        Raises:
            ValueError: If the context is invalid.
        """
        # Validate the format of the new context
        self._validate_context(extra_context)
        # Process and store the new context
        self._process_context(extra_context)

    def _update_references(self, references, seen_references, source_name, context_match, original_context, similarity_score):
        """
        Adds a new reference entry if it doesn't already exist.

        Args:
            references (List[Dict[str, Any]]): List of references to update.
            seen_references (set): Set of seen references to ensure uniqueness.
            source_name (str): Name of the source where the context was found.
            context_match (str): The matched context sentence.
            original_context (str): The original context text.
            similarity_score (float): The similarity score of the match.

        Returns:
            int: The reference number assigned to the new entry.
        """
        # Use a tuple of (source_name, context_match) as a unique key
        ref_key = (source_name, context_match)
        if ref_key not in seen_references:
            # Mark this reference as seen
            seen_references.add(ref_key)
            # Add a new reference entry
            new_ref = {
                "reference_number": len(references) + 1,
                "context": context_match,
                "original_context": original_context,
                "source_name": source_name,
            }
            references.append(new_ref)

        # Find and return the reference number for this context
        for ref in references:
            if ref["source_name"] == source_name and ref["context"] == context_match:
                return ref["reference_number"]

    def _match_with_fuzzy(self, response_segments: List[str]) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Matches response segments with context using fuzzy string matching.

        Args:
            response_segments (List[str]): Tokenized segments of the response text.

        Returns:
            Tuple[str, str, List[Dict[str, Any]]]: Contains:
                - Response text with added references.
                - JSON-formatted explanation of references.
                - List of attribution results.
        """
        attribution = []  # Stores matching results for each response segment
        textResponse = ''  # Final response with references added
        references = []  # List of reference metadata
        seen_references = set()  # Tracks unique references

        for response_segment in response_segments:
            original_segment = response_segment  # Keep a copy of the original segment

            # Use fuzzy matching to find the most similar context sentence
            match = process.extractOne(
                response_segment, self.context_sentences, scorer=fuzz.partial_ratio, score_cutoff=self.threshold
            )

            context_match, similarity_score, source_name, original_context = None, 0, None, None
            if match:
                # Extract match details
                context_match, similarity_score, _ = match
                info = self.sentence_info.get(context_match, {})
                source_name = info.get('source_name')
                original_context = info.get('original_context')

                # Add the reference to the list and update the segment
                ref_num = self._update_references(
                    references, seen_references, source_name, context_match, original_context, similarity_score
                )
                response_segment = self._insert_reference(response_segment, ref_num)
            else:
                original_context = None

            # Append the updated segment to the final response
            textResponse += response_segment + ' '

            # Save the attribution details
            attribution.append({
                "response_segment": original_segment,
                "context": context_match,
                "source_name": source_name,
                "similarity_score": similarity_score,
                "original_context": original_context,
            })

            # Print verbose debug information if enabled
            if self.verbose:
                self._print_verbose(attribution[-1], textResponse.strip(), json.dumps(references, indent=2))

        # Convert the references list to a JSON string
        textExplanation = json.dumps(references, indent=2)
        return textResponse.strip(), textExplanation, attribution

    def _generate_attribution(self, response_segments, similarity_matrix):
        """
        Generates attribution results using a similarity matrix.

        Args:
            response_segments (List[str]): Segments of the response text.
            similarity_matrix (np.ndarray): Matrix of similarity scores.

        Returns:
            Tuple[str, str, List[Dict[str, Any]]]: Contains:
                - Response text with added references.
                - JSON-formatted explanation of references.
                - List of attribution results.
        """
        attribution = []  # Tracks attribution data for each segment
        textResponse = ''  # Stores the final response with references
        references = []  # List of references
        seen_references = set()  # Tracks unique references

        for idx, response_segment in enumerate(response_segments):
            original_segment = response_segment  # Keep a copy of the original response segment

            # Retrieve similarity scores for this segment
            similarities = similarity_matrix[idx]
            max_similarity = np.max(similarities)  # Maximum similarity score
            best_match_idx = np.argmax(similarities)  # Index of the best match
            similarity_score = max_similarity * 100  # Convert to percentage

            context_match, source_name, original_context = None, None, None

            if similarity_score >= self.threshold:
                # Get the best matching context sentence and its metadata
                context_match = self.context_sentences[best_match_idx]
                info = self.sentence_info.get(context_match, {})
                source_name = info.get('source_name')
                original_context = info.get('original_context')

                # Add a reference for this match
                ref_num = self._update_references(
                    references, seen_references, source_name, context_match, original_context, similarity_score
                )

                # Append the reference number to the response segment
                response_segment = self._insert_reference(response_segment, ref_num)
            else:
                similarity_score = 0  # No significant match found

            # Append the updated segment to the final response
            textResponse += response_segment + ' '

            # Save the attribution details
            attribution.append({
                "response_segment": original_segment,
                "context": context_match,
                "source_name": source_name,
                "similarity_score": similarity_score,
                "original_context": original_context,
            })

            # Print verbose debug information if enabled
            if self.verbose:
                self._print_verbose(attribution[-1], textResponse.strip(), json.dumps(references, indent=2))

        # Convert references to JSON
        textExplanation = json.dumps(references, indent=2)
        return textResponse.strip(), textExplanation, attribution

    def _match_with_embeddings(self, response_segments: List[str]) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Matches response segments with context using embeddings.

        Args:
            response_segments (List[str]): Tokenized segments of the response text.

        Returns:
            Tuple[str, str, List[Dict[str, Any]]]: Contains:
                - Response text with added references.
                - JSON-formatted explanation of references.
                - List of attribution results.
        """
        references = []  # List of references
        seen_references = set()  # Tracks unique references

        # Generate embeddings for the response segments
        response_embeddings = self.embedding_model.encode(response_segments, convert_to_tensor=True).cpu()

        # Compute similarity scores between response embeddings and context embeddings
        similarity_matrix = cosine_similarity(response_embeddings, self.context_embeddings)

        # Generate the attribution results using the similarity matrix
        textResponse, textExplanation, attribution = self._generate_attribution(response_segments, similarity_matrix)

        return textResponse, textExplanation, attribution
    
    def attribute_response_to_context(self, response: str) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Attributes segments of a response to the most similar segments in the provided context.

        Parameters:
        - response (str): The LLM-generated response to attribute.

        Returns:
        - A tuple containing:
            - textResponse (str): The response with reference numbers added.
            - textExplanation (str): JSON string of references.
            - attribution (List[Dict[str, Any]]): A list of dictionaries containing attribution results.
        """
        self._validate_parameters()

        if not isinstance(response, str):
            raise ValueError(f"The 'response' parameter must be a string. Received type {type(response).__name__}.")

        response_segments = sent_tokenize(response)
        if not response_segments:
            raise ValueError("The 'response' parameter does not contain any sentences after tokenization.")

        if self.use_embeddings:
            return self._match_with_embeddings(response_segments)
        else:
            return self._match_with_fuzzy(response_segments)


if __name__ == "__main__":
    # Example usage
    explainer = RagExplainer(
        threshold=40.0,
        verbose=False,
        tokenize_context=True,
        use_embeddings=True
    )

    # Add English context
    text_context = [
        ("English Book", "The solar system consists of the Sun and objects bound to it."),
        ("English Book", "This includes eight planets, their moons, and smaller objects.")
    ]
    explainer.add_to_context(text_context)

    # Add Spanish context
    spanish_context = [
        ("Spanish Article", "El Sol es la estrella en el centro del sistema solar.")
    ]
    explainer.add_to_context(spanish_context)

    # Add French context
    french_context = [
        ("French Article", "L'atmosphère terrestre est cruciale pour la vie sur Terre.")
    ]
    explainer.add_to_context(french_context)

    # Add German context
    german_context = [
        ("German Article", "Die industrielle Revolution veränderte Gesellschaften radikal.")
    ]
    explainer.add_to_context(german_context)

    # Add JSON context
    json_multilingual = [
        ("Json Data", '[{"Machine_name": "Machine_A", "KPI_name": "Temperatura", "Predicted_value": "22", "Measure_unit": "Celsius", "Date_prediction": "12/12/2024", "Forecast": true}, {"Machine_name": "Machine_B", "KPI_name": "Pression", "Predicted_value": "1012", "Measure_unit": "hPa", "Date_prediction": "13/12/2024", "Forecast": true}]')
    ]
    explainer.add_to_context(json_multilingual)

    # Multilingual response
    response = (
        "The solar system is centered on the Sun. "
        "El Sol es la estrella central del sistema solar. "
        "L'atmosphère terrestre est essentielle. "
        "Die industrielle Revolution hat die Gesellschaft verändert. "
        "Machine_A ha un Temperatura di 22 Gradi Celsius. "
        "El Sol es la estrella central del sistema solar. "
    )


    textResponse, textExplanation, attribution_results = explainer.attribute_response_to_context(response)

    # Output the results
    print("\nFinal Outputs:")
    print("Text Response:")
    print(textResponse)
    print("\nText Explanation (JSON):")

    print(textExplanation)
    print("\nAttribution Results:")
    for result in attribution_results:
        print(result)
