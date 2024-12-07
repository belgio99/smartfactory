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
        print("\nText Explanation (JSON):")

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

        if not isinstance(self.threshold, (int, float)) or not (0 <= self.threshold <= 100):
            raise ValueError(f"The 'threshold' parameter must be a number between 0 and 100. Received {self.threshold}.")

        if not isinstance(self.verbose, bool):
            raise ValueError(f"The 'verbose' parameter must be a boolean. Received type {type(self.verbose).__name__}.")

    def _insert_reference(self, response_segment: str, ref_num: int) -> str:
        """
        Inserts the reference number before periods and commas at the end of the response segment.
        """
        if response_segment.endswith(('.', ',')):
            return response_segment[:-1] + f'[{ref_num}]' + response_segment[-1]
        else:
            return response_segment + f'[{ref_num}]'

    def _parse_json_context(self, ctx: str) -> List[str]:
        """
        Parses a JSON string context into a list of "sentences."
        """
        try:
            data = json.loads(ctx)
        except json.JSONDecodeError:
            return []

        def format_object(obj: dict) -> str:
            lines = []
            for k, v in obj.items():
                lines.append(f'"{k}": "{v}"')
            return "\n   " + "\n   ".join(lines)

        if isinstance(data, list):
            sentences = []
            for item in data:
                if isinstance(item, dict):
                    formatted = format_object(item)
                    if len(formatted.strip()) >= 10:
                        sentences.append(formatted)
                else:
                    if len(str(item).strip()) >= 10:
                        sentences.append(str(item))
            return sentences
        elif isinstance(data, dict):
            formatted = format_object(data)
            if len(formatted.strip()) >= 10:
                return [formatted]
            else:
                return []
        else:
            return []

    def _process_context(self, context: List[Tuple[str, str]]):
        """
        Processes the context by tokenizing (if applicable) and adding to the internal data structures.
        """
        new_context_sentences = []

        for idx, (source_name, ctx) in enumerate(context):
            json_sentences = self._parse_json_context(ctx)

            if json_sentences:
                ctx_strings = json_sentences
            else:
                if self.tokenize_context:
                    ctx_strings = sent_tokenize(ctx)
                else:
                    ctx_strings = [ctx]

            if not ctx_strings:
                raise ValueError(f"The context at index {idx} is empty after tokenization or JSON parsing.")

            for string in ctx_strings:
                if len(string.strip()) < 10:
                    continue

                if string not in self.sentence_info:

                    self.context_sentences.append(string)
                    self.sentence_info[string] = {
                        'source_name': source_name,
                        'original_context': ctx
                    }
                    new_context_sentences.append(string)

        if self.use_embeddings and new_context_sentences:
            new_embeddings = self.embedding_model.encode(new_context_sentences, convert_to_tensor=True)

            if self.context_embeddings is not None:
                self.context_embeddings = np.concatenate((self.context_embeddings, new_embeddings), axis=0)
            else:
                self.context_embeddings = new_embeddings

    def add_to_context(self, extra_context: List[Tuple[str, str]]):
        """
        Adds extra context to the existing context, avoiding duplicates.
        """
        self._validate_context(extra_context)
        self._process_context(extra_context)

    def _update_references(self, references, seen_references, source_name, context_match, original_context, similarity_score):
        """
        Updates the references list with a new reference entry if it doesn't already exist.

        Parameters:
        - references: List of references (each reference is a dict).
        - seen_references: A set of tuples (source_name, context_match) to track uniqueness.
        - source_name: Source name of the matched context.
        - context_match: Matched context sentence.
        - original_context: The original context from which the matched sentence was derived.
        - similarity_score: The similarity score for this match (unused in final reference structure).

        Returns:
        - ref_num: Reference number assigned (1-based index).
        """
        ref_key = (source_name, context_match)
        if ref_key not in seen_references:
            seen_references.add(ref_key)
            new_ref = {
                "reference_number": len(references) + 1,
                "context": context_match,
                "original_context": original_context,
                "source_name": source_name
                # Removed "similarity_score" from the reference
            }
            references.append(new_ref)

        # Find the reference to get its number
        for ref in references:
            if ref["source_name"] == source_name and ref["context"] == context_match:
                return ref["reference_number"]

    def _match_with_fuzzy(self, response_segments: List[str]) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Matches response segments with context using fuzzy matching.
        """
        attribution = []
        textResponse = ''
        references = []
        seen_references = set()

        for response_segment in response_segments:
            original_segment = response_segment

            match = process.extractOne(
                response_segment, self.context_sentences, scorer=fuzz.partial_ratio, score_cutoff=self.threshold
            )

            context_match, similarity_score, source_name, original_context = None, 0, None, None
            if match:
                context_match, similarity_score, _ = match
                info = self.sentence_info.get(context_match, {})
                source_name = info.get('source_name')
                original_context = info.get('original_context')

                ref_num = self._update_references(
                    references,
                    seen_references,
                    source_name,
                    context_match,
                    original_context,
                    similarity_score
                )
                response_segment = self._insert_reference(response_segment, ref_num)
            else:
                original_context = None

            textResponse += response_segment + ' '

            attribution.append({
                "response_segment": original_segment,
                "context": context_match,
                "source_name": source_name,
                "similarity_score": similarity_score,
                "original_context": original_context
            })

            if self.verbose:
                self._print_verbose(attribution[-1], textResponse.strip(), json.dumps(references, indent=2))

        # Convert references list to JSON
        textExplanation = json.dumps(references, indent=2)
        return textResponse.strip(), textExplanation, attribution


    def _generate_attribution(self, response_segments, similarity_matrix):
        """
        Generates the attribution results based on similarity matrix.
        """
        attribution = []
        textResponse = ''
        references = []
        seen_references = set()

        for idx, response_segment in enumerate(response_segments):
            original_segment = response_segment
            similarities = similarity_matrix[idx]
            max_similarity = np.max(similarities)
            best_match_idx = np.argmax(similarities)
            similarity_score = max_similarity * 100

            context_match, source_name, original_context = None, None, None

            if similarity_score >= self.threshold:
                context_match = self.context_sentences[best_match_idx]
                info = self.sentence_info.get(context_match, {})
                source_name = info.get('source_name')
                original_context = info.get('original_context')

                ref_num = self._update_references(
                    references,
                    seen_references,
                    source_name,
                    context_match,
                    original_context,
                    similarity_score
                )

                response_segment = self._insert_reference(response_segment, ref_num)
            else:
                similarity_score = 0

            textResponse += response_segment + ' '

            attribution.append({
                "response_segment": original_segment,
                "context": context_match,
                "source_name": source_name,
                "similarity_score": similarity_score,
                "original_context": original_context
            })

            if self.verbose:
                self._print_verbose(attribution[-1], textResponse.strip(), json.dumps(references, indent=2))

        # Convert references list to JSON
        textExplanation = json.dumps(references, indent=2)
        return textResponse.strip(), textExplanation, attribution

    def _match_with_embeddings(self, response_segments: List[str]) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Matches response segments with context using embeddings.
        """
        references = []
        seen_references = set()

        # Generate embeddings for response segments
        response_embeddings = self.embedding_model.encode(response_segments, convert_to_tensor=True)
        # Compute cosine similarity
        similarity_matrix = cosine_similarity(response_embeddings, self.context_embeddings)
        # Generate attribution
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
