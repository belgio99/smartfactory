from typing import List, Dict, Any, Tuple
import numpy as np
import json
from rapidfuzz import process, fuzz
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK 'punkt' tokenizer is downloaded upon module import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Import for embeddings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class RagExplainer:
    def __init__(
        self,
        context: List[Tuple[str, str]] = [],
        threshold: float = 50.0,
        verbose: bool = False,
        tokenize_context: bool = True,
        use_embeddings: bool = True
    ):
        """
        Initializes the RagExplainer object with the given parameters.

        Parameters:
        - context: List of tuples containing source name and context string.
        - threshold: Similarity threshold for matching (0 to 100).
        - verbose: Flag to enable verbose output.
        - tokenize_context: If True, context strings are tokenized into sentences.
        - use_embeddings: If True, use embeddings for similarity matching.
        """
        self.threshold = threshold
        self.verbose = verbose
        self.tokenize_context = tokenize_context
        self.use_embeddings = use_embeddings

        # Initialize context data structures
        self.context_sentences = []        # List to store unique context sentences or strings
        self.sentence_info = {}            # Mapping from sentence to {'source_name', 'original_context'}
        self.context_embeddings = None     # Embeddings for context sentences (used if use_embeddings=True)

        # Initialize embedding model if needed
        # Changed to a multilingual model:
        if self.use_embeddings:
            self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        else:
            self.embedding_model = None

        # Process initial context (if any)
        self.add_to_context(context)

    def _print_verbose(self, result, textResponse, textExplanation):
        """
        Prints verbose output for debugging purposes.
        """
        print(f"Response Segment: {result['response_segment']}")
        if result['context']:
            print(f"Attributed Context: {result['context']}")
            print(f"Source Name: {result['source_name']}")
            print(f"Original Context: {result['original_context']}")
            print(f"Similarity Score: {result['similarity_score']:.2f}%")
        else:
            print("No context meets the similarity threshold.")
            print(f"Highest Similarity Score: {result['similarity_score']:.2f}%")
        print("-" * 50)
        print("\nText Response:")
        print(textResponse)
        print("\nText Explanation:")
        print(textExplanation)
        print("-" * 50)

    def _validate_context(self, context):
        """
        Validates the context input to ensure it is in the correct format.
        """
        if not isinstance(context, list):
            raise ValueError(f"The 'context' parameter must be a list of tuples. Received type {type(context).__name__}.")
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
        Validates the threshold and verbose parameters.
        """
        # Validate threshold
        if not isinstance(self.threshold, (int, float)) or not (0 <= self.threshold <= 100):
            raise ValueError(f"The 'threshold' parameter must be a number between 0 and 100. Received {self.threshold}.")

        # Validate verbose
        if not isinstance(self.verbose, bool):
            raise ValueError(f"The 'verbose' parameter must be a boolean. Received type {type(self.verbose).__name__}.")

    def _insert_reference(self, response_segment: str, ref_num: int) -> str:
        """
        Inserts the reference number before periods and commas at the end of the response segment.

        Parameters:
        - response_segment: The segment of the response text.
        - ref_num: The reference number to insert.

        Returns:
        - The response segment with the reference number inserted appropriately.
        """
        # Check if the segment ends with a period or comma
        if response_segment.endswith(('.', ',')):
            # Insert the reference number before the punctuation
            return response_segment[:-1] + f'[{ref_num}]' + response_segment[-1]
        else:
            # No punctuation at the end; add the reference number at the end
            return response_segment + f'[{ref_num}]'

    def _parse_json_context(self, ctx: str) -> List[str]:
        """
        Parses a JSON string context into a list of "sentences."

        If the JSON is a list of objects, each object becomes one sentence.
        If the JSON is a single object, it becomes one sentence.
        Otherwise, returns an empty list if parsing fails.

        Returns:
        - A list of context sentences.
        """
        try:
            data = json.loads(ctx)
        except json.JSONDecodeError:
            # Not valid JSON
            return []

        # Helper function to format a single object
        def format_object(obj: dict) -> str:
            # Convert a dict into a multiline string of key-value pairs
            lines = []
            for k, v in obj.items():
                lines.append(f'"{k}": "{v}"')
            # Join lines with newline and indent
            return "\n   " + "\n   ".join(lines)

        if isinstance(data, list):
            # Each item in the list is treated as a separate context sentence
            sentences = []
            for item in data:
                if isinstance(item, dict):
                    # Format the dict as multiline
                    formatted = format_object(item)
                    if len(formatted.strip()) >= 10:
                        sentences.append(formatted)
                else:
                    if len(str(item).strip()) >= 10:
                        sentences.append(str(item))
            return sentences
        elif isinstance(data, dict):
            # Single dict object
            formatted = format_object(data)
            if len(formatted.strip()) >= 10:
                return [formatted]
            else:
                return []
        else:
            # If data is something else (like a string or number), return empty
            return []

    def _process_context(self, context: List[Tuple[str, str]]):
        """
        Processes the context by tokenizing (if applicable) and adding to the internal data structures.

        Parameters:
        - context: List of tuples containing source name and context string.
        """
        new_context_sentences = []  # To store new context sentences added in this call

        for idx, (source_name, ctx) in enumerate(context):
            # Check if the context might be JSON
            json_sentences = self._parse_json_context(ctx)

            if json_sentences:
                # If JSON parsed successfully, use json_sentences as the context sentences
                ctx_strings = json_sentences
            else:
                # If not JSON, then use normal text tokenization
                if self.tokenize_context:
                    ctx_strings = sent_tokenize(ctx)
                else:
                    ctx_strings = [ctx]

            if not ctx_strings:
                raise ValueError(f"The context at index {idx} is empty after tokenization or JSON parsing.")

            for string in ctx_strings:
                # Only add if length of the string is at least 10 characters
                if len(string.strip()) < 10:
                    continue

                if string not in self.sentence_info:
                    # Add the new sentence to the list and mapping
                    self.context_sentences.append(string)
                    self.sentence_info[string] = {
                        'source_name': source_name,
                        'original_context': ctx
                    }
                    new_context_sentences.append(string)

        # If embeddings are used, generate embeddings for new context sentences
        if self.use_embeddings and new_context_sentences:
            # Generate embeddings for the new sentences
            new_embeddings = self.embedding_model.encode(new_context_sentences, convert_to_tensor=True)
            # Concatenate with existing embeddings if any
            if self.context_embeddings is not None:
                self.context_embeddings = np.concatenate((self.context_embeddings, new_embeddings), axis=0)
            else:
                self.context_embeddings = new_embeddings

    def add_to_context(self, extra_context: List[Tuple[str, str]]):
        """
        Adds extra context to the existing context, avoiding duplicates.

        Parameters:
        - extra_context: List of tuples containing source name and context string.
        """
        # Validate the extra context input
        self._validate_context(extra_context)
        # Process and add the extra context
        self._process_context(extra_context)

    def _match_with_embeddings(self, response_segments: List[str]) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Matches response segments with context using embeddings.

        Parameters:
        - response_segments: List of segmented response strings.

        Returns:
        - A tuple containing textResponse, textExplanation, and attribution list.
        """
        # Generate embeddings for response segments
        response_embeddings = self.embedding_model.encode(response_segments, convert_to_tensor=True)
        # Compute cosine similarity between response embeddings and context embeddings
        similarity_matrix = cosine_similarity(response_embeddings, self.context_embeddings)
        # Generate the attribution results based on the similarity matrix
        return self._generate_attribution(response_segments, similarity_matrix)

    def _match_with_fuzzy(self, response_segments: List[str]) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Matches response segments with context using fuzzy matching.

        Parameters:
        - response_segments: List of segmented response strings.

        Returns:
        - A tuple containing textResponse, textExplanation, and attribution list.
        """
        attribution = []  # List to store attribution results
        references = []   # List to keep track of references added
        textResponse = '' # The response text with references added
        textExplanation = '' # The explanation text containing the references

        for response_segment in response_segments:
            original_segment = response_segment  # Store the original segment without modifications
            # Use RapidFuzz to find the best match in the context sentences
            match = process.extractOne(
                response_segment, self.context_sentences, scorer=fuzz.partial_ratio, score_cutoff=self.threshold
            )

            # Initialize default values
            context_match, similarity_score, source_name, original_context = None, 0, None, None

            if match:
                # Unpack the match result
                context_match, similarity_score, _ = match
                # Get the source info for the matched context
                info = self.sentence_info.get(context_match, {})
                source_name = info.get('source_name')
                original_context = info.get('original_context')
                # Update references and get the reference number
                ref_num, textExplanation = self._update_references(references, source_name, context_match, textExplanation)
                # Insert the reference number into the response segment
                response_segment = self._insert_reference(response_segment, ref_num)

            else:
                original_context = None

            # Append the modified response segment to the textResponse
            textResponse += response_segment + ' '

            # Prepare the attribution result for this segment
            attribution.append({
                "response_segment": original_segment,  # Original response segment without references
                "context": context_match,              # Matched context sentence
                "source_name": source_name,            # Source name of the context
                "similarity_score": similarity_score,  # Similarity score
                "original_context": original_context   # Original context before tokenization
            })

            # If verbose mode is on, print detailed information
            if self.verbose:
                self._print_verbose(attribution[-1], textResponse.strip(), textExplanation.strip())

        # Return the results, stripping any extra whitespace
        return textResponse.strip(), textExplanation.strip(), attribution

    def _update_references(self, references, source_name, context_match, textExplanation):
        """
        Updates the references list and textExplanation with new references.

        Parameters:
        - references: Current list of references.
        - source_name: Source name of the matched context.
        - context_match: Matched context sentence.
        - textExplanation: Current text explanation.

        Returns:
        - ref_num: Reference number assigned.
        - textExplanation: Updated text explanation.
        """
        if (source_name, context_match) not in references:
            # Add new reference to the list
            references.append((source_name, context_match))
            # Update the textExplanation with the new reference
            textExplanation += f'[{len(references)}] {source_name}: {context_match}\n'
        # Get the reference number (1-based index)
        ref_num = references.index((source_name, context_match)) + 1
        return ref_num, textExplanation

    def _generate_attribution(self, response_segments, similarity_matrix):
        """
        Generates the attribution results based on similarity matrix.

        Parameters:
        - response_segments: List of segmented response strings.
        - similarity_matrix: Matrix of similarity scores between response and context embeddings.

        Returns:
        - A tuple containing textResponse, textExplanation, and attribution list.
        """
        attribution = []      # List to store attribution results
        references = []       # List to keep track of references added
        textResponse = ''     # The response text with references added
        textExplanation = ''  # The explanation text containing the references

        for idx, response_segment in enumerate(response_segments):
            original_segment = response_segment  # Store the original segment
            similarities = similarity_matrix[idx]  # Similarities for current response segment
            max_similarity = np.max(similarities)  # Maximum similarity score
            best_match_idx = np.argmax(similarities)  # Index of the best matching context sentence
            similarity_score = max_similarity * 100   # Convert similarity score to percentage

            # Initialize default values
            context_match, source_name, original_context = None, None, None

            if similarity_score >= self.threshold:
                # Get the best matching context sentence
                context_match = self.context_sentences[best_match_idx]
                # Get the source info for the context
                info = self.sentence_info.get(context_match, {})
                source_name = info.get('source_name')
                original_context = info.get('original_context')
                # Update references and get the reference number
                ref_num, textExplanation = self._update_references(references, source_name, context_match, textExplanation)
                # Insert the reference number into the response segment
                response_segment = self._insert_reference(response_segment, ref_num)
            else:
                similarity_score = 0

            # Append the modified response segment to the textResponse
            textResponse += response_segment + ' '

            # Prepare the attribution result for this segment
            attribution.append({
                "response_segment": original_segment,  # Original response segment without references
                "context": context_match,              # Matched context sentence
                "source_name": source_name,            # Source name of the context
                "similarity_score": similarity_score,  # Similarity score
                "original_context": original_context   # Original context before tokenization
            })

            # If verbose mode is on, print detailed information
            if self.verbose:
                self._print_verbose(attribution[-1], textResponse.strip(), textExplanation.strip())

        # Return the results, stripping any extra whitespace
        return textResponse.strip(), textExplanation.strip(), attribution

    def attribute_response_to_context(self, response: str) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Attributes segments of a response to the most similar segments in the provided context.

        Parameters:
        - response (str): The LLM-generated response to attribute.

        Returns:
        - A tuple containing:
            - textResponse (str): The response with reference numbers added.
            - textExplanation (str): The references with corresponding numbers.
            - attribution (List[Dict[str, Any]]): A list of dictionaries containing attribution results.

        Raises:
        - ValueError: If inputs are not of the expected types or formats.
        """
        # Validate parameters
        self._validate_parameters()

        # Validate response input
        if not isinstance(response, str):
            raise ValueError(f"The 'response' parameter must be a string. Received type {type(response).__name__}.")

        # Tokenize the response into sentences
        response_segments = sent_tokenize(response)
        if not response_segments:
            raise ValueError("The 'response' parameter does not contain any sentences after tokenization.")

        # Choose the matching method based on use_embeddings flag
        if self.use_embeddings:
            # Use embedding-based matching
            return self._match_with_embeddings(response_segments)
        else:
            # Use fuzzy string matching
            return self._match_with_fuzzy(response_segments)


if __name__ == "__main__":
    # Example usage
    # Now we turn use_embeddings to True to leverage the multilingual model.
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
    # Example: Short explanation about the sun in Spanish
    spanish_context = [
        ("Spanish Article", "El Sol es la estrella en el centro del sistema solar.")
    ]
    explainer.add_to_context(spanish_context)

    # Add French context
    # Example: A statement about the importance of the atmosphere in French
    french_context = [
        ("French Article", "L'atmosphère terrestre est cruciale pour la vie sur Terre.")
    ]
    explainer.add_to_context(french_context)

    # Add German context
    german_context = [
        ("German Article", "Die industrielle Revolution veränderte Gesellschaften radikal.")
    ]
    explainer.add_to_context(german_context)

    # Add JSON context with multilingual content
    json_multilingual = [
        ("Json Data", '[{"Machine_name": "Machine_A", "KPI_name": "Temperatura", "Predicted_value": "22", "Measure_unit": "Celsius", "Date_prediction": "12/12/2024", "Forecast": true}, {"Machine_name": "Machine_B", "KPI_name": "Pression", "Predicted_value": "1012", "Measure_unit": "hPa", "Date_prediction": "13/12/2024", "Forecast": true}]')
    ]
    explainer.add_to_context(json_multilingual)

    # Multilingual response referencing various languages and machine data
    response = (
        "The solar system is centered on the Sun. "
        "El Sol es la estrella central del sistema solar. "
        "L'atmosphère terrestre est essentielle. "
        "Die industrielle Revolution hat die Gesellschaft verändert. "
        "Machine_A ha un Temperatura di 22 Gradi Celsius."
    )

    # Call the attribute_response_to_context method
    textResponse, textExplanation, attribution_results = explainer.attribute_response_to_context(response)

    # Output the results
    print("\nFinal Outputs:")
    print("Text Response:")
    print(textResponse)
    print("\nText Explanation:")
    print(textExplanation)
    print("\nAttribution Results:")
    for result in attribution_results:
        print(result)
