from typing import List, Dict, Any, Tuple
import numpy as np
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
        threshold: float = 60.0,
        verbose: bool = False,
        tokenize_context: bool = True,
        use_embeddings: bool = False
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
        self.sentence_to_source = {}       # Mapping from sentence to its source name
        self.context_embeddings = None     # Embeddings for context sentences (used if use_embeddings=True)

        # Initialize embedding model if needed
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') if self.use_embeddings else None

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

    def _process_context(self, context: List[Tuple[str, str]]):
        """
        Processes the context by tokenizing (if applicable) and adding to the internal data structures.

        Parameters:
        - context: List of tuples containing source name and context string.
        """
        new_context_sentences = []  # To store new context sentences added in this call

        for idx, (source_name, ctx) in enumerate(context):
            # Tokenize context string into sentences if tokenize_context is True
            ctx_strings = sent_tokenize(ctx) if self.tokenize_context else [ctx]
            if not ctx_strings:
                raise ValueError(f"The context at index {idx} is empty after tokenization.")

            for string in ctx_strings:
                if string not in self.sentence_to_source:
                    # Add the new sentence to the list and mapping
                    self.context_sentences.append(string)
                    self.sentence_to_source[string] = source_name
                    new_context_sentences.append(string)
                else:
                    # Sentence already exists; skip to avoid duplicates
                    pass

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
            context_match, similarity_score, source_name = None, 0, None

            if match:
                # Unpack the match result
                context_match, similarity_score, _ = match
                # Get the source name for the matched context
                source_name = self.sentence_to_source.get(context_match)
                # Update references and get the reference number
                ref_num, textExplanation = self._update_references(references, source_name, context_match, textExplanation)
                # Insert the reference number into the response segment
                response_segment = self._insert_reference(response_segment, ref_num)

            # Append the modified response segment to the textResponse
            textResponse += response_segment + ' '

            # Prepare the attribution result for this segment
            attribution.append({
                "response_segment": original_segment,  # Original response segment without references
                "context": context_match,              # Matched context sentence
                "source_name": source_name,            # Source name of the context
                "similarity_score": similarity_score   # Similarity score
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

            if similarity_score >= self.threshold:
                # Get the best matching context sentence
                context_match = self.context_sentences[best_match_idx]
                # Get the source name for the context
                source_name = self.sentence_to_source.get(context_match)
                # Update references and get the reference number
                ref_num, textExplanation = self._update_references(references, source_name, context_match, textExplanation)
                # Insert the reference number into the response segment
                response_segment = self._insert_reference(response_segment, ref_num)
            else:
                # No match found above threshold
                context_match, source_name, similarity_score = None, None, 0

            # Append the modified response segment to the textResponse
            textResponse += response_segment + ' '

            # Prepare the attribution result for this segment
            attribution.append({
                "response_segment": original_segment,  # Original response segment without references
                "context": context_match,              # Matched context sentence
                "source_name": source_name,            # Source name of the context
                "similarity_score": similarity_score   # Similarity score
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
    # Initialize RagExplainer with use_embeddings=True
    explainer = RagExplainer(
        threshold=55.0,
        verbose=False,
        tokenize_context=True,
        use_embeddings=True
    )

    # Add initial context
    context = [
        ("Astronomy Book", "The solar system consists of the Sun and the celestial objects that are gravitationally bound to it."),
        ("Astronomy Book", "This includes eight planets, their moons, dwarf planets, and countless asteroids and comets."),
        ("Astronomy Book", "The Sun, a G-type main-sequence star, accounts for 99.86% of the solar system's mass."),
        ("Astronomy Book", "It is the central body around which all planets orbit."),
        ("Astronomy Book", "The inner planets, Mercury, Venus, Earth, and Mars, are terrestrial planets with rocky surfaces."),
        ("Astronomy Book", "The outer planets, Jupiter, Saturn, Uranus, and Neptune, are gas and ice giants."),
        ("Earth Science Book", "The Earth's atmosphere is composed of 78% nitrogen, 21% oxygen, and trace amounts of other gases such as argon and carbon dioxide."),
        ("Earth Science Book", "It provides the air we breathe and protects us from harmful solar radiation."),
        ("Earth Science Book", "The ozone layer, part of the Earth's stratosphere, absorbs the majority of the Sun's ultraviolet radiation."),
        ("Earth Science Book", "Earth's surface is mostly covered by water. It is the only known planet to support life."),
        ("Earth Science Book", "Its magnetic field shields it from the solar wind, preserving its atmosphere and enabling diverse ecosystems."),
        ("AI Article", "Artificial intelligence (AI) has rapidly advanced in recent years."),
        ("AI Article", "It is impacting various industries including healthcare, finance, and transportation."),
        ("AI Article", "Machine learning, a subset of AI, focuses on developing algorithms that allow computers to learn from data without being explicitly programmed."),
        ("AI Article", "Deep learning, a specialized form of machine learning, utilizes artificial neural networks to process complex data and achieve remarkable results."),
        ("AI Article", "It excels in fields like natural language processing and image recognition."),
        ("AI Article", "Ethical considerations in AI development, such as bias and privacy, remain critical concerns."),
        ("History Book", "The history of human civilization spans thousands of years."),
        ("History Book", "It is marked by the development of writing, agriculture, and industry."),
        ("History Book", "Ancient civilizations like Mesopotamia, Egypt, and the Indus Valley contributed to the foundations of modern society."),
        ("History Book", "They introduced systems of governance, trade, and cultural exchange."),
        ("History Book", "The Industrial Revolution, beginning in the late 18th century, transformed economies and societies."),
        ("History Book", "It ushered in an era of rapid technological progress. Today, globalization connects the world more than ever."),
        ("History Book", "It enables unprecedented collaboration and exchange.")
    ]

    explainer.add_to_context(context)

    # Add extra context
    extra_context = [
        ("New Source", "Mars is known as the Red Planet."),
        ("New Source", "It is the fourth planet from the Sun."),
    ]

    explainer.add_to_context(extra_context)

    response = (
        "Artificial intelligence has revolutionized industries by improving processes in fields like transportation and healthcare. "
        "For instance, machine learning allows systems to adapt and learn without being explicitly programmed. "
        "The Earth's atmosphere is vital for life, with nitrogen and oxygen making up its majority. "
        "The Sun, central to our solar system, has a mass that constitutes the majority of the system. "
        "Planets like Jupiter and Saturn are gas giants, while Earth supports life due to its unique atmosphere and magnetic field. "
        "Historical events such as the Industrial Revolution reshaped human societies, laying the groundwork for today's interconnected world. "
        "My name is Alex, and I'm fascinated by these topics. "
        "The Sun, central to our solar system, has a mass that constitutes the majority of the system."
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
