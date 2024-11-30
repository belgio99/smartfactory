from typing import List, Dict, Any, Tuple
from rapidfuzz import process, fuzz
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK 'punkt' tokenizer is downloaded upon module import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class ResponseAttributor:
    def __init__(self, context: List[Tuple[str, str]], threshold: float = 60.0, verbose: bool = False):
        """
        Initializes the ResponseAttributor object with the given context, threshold, and verbose flag.
        """
        self.context = context
        self.threshold = threshold
        self.verbose = verbose

        # Input validation
        self._validate_inputs()

        # Segment the context into sentences, maintaining source names
        self.context_segments = []
        for idx, (source_name, ctx) in enumerate(self.context):
            ctx_sentences = sent_tokenize(ctx)
            if not ctx_sentences:
                raise ValueError(f"The context at index {idx} does not contain any sentences after tokenization.")
            for sentence in ctx_sentences:
                self.context_segments.append((source_name, sentence))

        if not self.context_segments:
            raise ValueError("No context sentences found after tokenization.")

    def _print_verbose(self, result, textResponse, textExplanation):
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

    def _validate_inputs(self):
        """
        Validates the inputs to the ResponseAttributor class.

        Raises:
            ValueError: If any of the inputs are invalid.
        """
        # Validate context
        if not isinstance(self.context, list):
            raise ValueError(f"The 'context' parameter must be a list of tuples. Received type {type(self.context).__name__}.")
        else:
            for i, item in enumerate(self.context):
                if not (isinstance(item, tuple) and len(item) == 2):
                    raise ValueError(f"All items in the 'context' list must be tuples of (source_name, context_string). Item at index {i} is invalid.")
                source_name, ctx = item
                if not isinstance(source_name, str):
                    raise ValueError(f"The source name at index {i} must be a string. Received type {type(source_name).__name__}.")
                if not isinstance(ctx, str):
                    raise ValueError(f"The context string at index {i} must be a string. Received type {type(ctx).__name__}.")

        # Validate threshold
        if not isinstance(self.threshold, (int, float)):
            raise ValueError(f"The 'threshold' parameter must be a number (int or float). Received type {type(self.threshold).__name__}.")
        elif not (0 <= self.threshold <= 100):
            raise ValueError(f"The 'threshold' parameter must be between 0 and 100. Received {self.threshold}.")

        # Validate verbose
        if not isinstance(self.verbose, bool):
            raise ValueError(f"The 'verbose' parameter must be a boolean. Received type {type(self.verbose).__name__}.")

    def _insert_reference(self, response_segment: str, ref_num: int) -> str:
        """
        Inserts the reference number before periods and commas at the end of the response segment.
        """
        # If the segment ends with a period or comma
        if response_segment.endswith(('.', ',')):
            # Insert the reference number before the punctuation
            return response_segment[:-1] + f'[{ref_num}]' + response_segment[-1]
        else:
            # No period or comma at the end, just add the reference number at the end
            return response_segment + f'[{ref_num}]'

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
        # Validate response
        if not isinstance(response, str):
            raise ValueError(f"The 'response' parameter must be a string. Received type {type(response).__name__}.")

        # Step 1: Segment the response into sentences
        response_segments = sent_tokenize(response)
        if not response_segments:
            raise ValueError("The 'response' parameter does not contain any sentences after tokenization.")

        # Step 2: Initialize variables
        attribution = []
        references = []
        textResponse = ''
        textExplanation = ''

        # Prepare data for matching: context_sentences (list of strings), mapping to source names
        context_sentences = [sentence for (_, sentence) in self.context_segments]

        # Map from context_sentence to source_name
        sentence_to_source = {sentence: source_name for (source_name, sentence) in self.context_segments}

        # Step 3: Compare each response segment with all context segments
        for response_segment in response_segments:
            # Use RapidFuzz to find the best match for the response segment
            match = process.extractOne(
                response_segment, context_sentences, scorer=fuzz.token_set_ratio, score_cutoff=self.threshold
            )

            # Initialize default values
            context_match = None
            similarity_score = 0
            source_name = None

            # If a match is found, unpack the values and build textResponse and textExplanation during the loop
            if match:
                context_match, similarity_score, _ = match
                source_name = sentence_to_source.get(context_match)
                if (source_name, context_match) not in references:
                    # Add reference to textExplanation
                    references.append((source_name, context_match))
                    textExplanation += f'[{len(references)}] {source_name}: {context_match}\n'
                # Add reference number to response segment
                ref_num = references.index((source_name, context_match)) + 1

                # Insert reference number before punctuation
                response_segment = self._insert_reference(response_segment, ref_num)
                textResponse += response_segment + ' '
            else:
                textResponse += response_segment + ' '

            # Prepare the result dictionary
            result = {
                "response_segment": response_segment,
                "context": context_match,
                "source_name": source_name,
                "similarity_score": similarity_score
            }

            # Append the result to the attribution list
            attribution.append(result)

            # Verbose output
            if self.verbose:
                self._print_verbose(result, textResponse.strip(), textExplanation.strip())

        # Remove trailing whitespace
        textResponse = textResponse.strip()
        textExplanation = textExplanation.strip()

        return textResponse, textExplanation, attribution


if __name__ == "__main__":
    # Example context and response with large text
    context = [
        # (source_name, context_string)
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

    response = ("Artificial intelligence has revolutionized industries by improving processes in fields like transportation and healthcare. "
                "For instance, machine learning allows systems to adapt and learn without being explicitly programmed. "
                "The Earth's atmosphere is vital for life, with nitrogen and oxygen making up its majority. "
                "The Sun, central to our solar system, has a mass that constitutes the majority of the system. "
                "Planets like Jupiter and Saturn are gas giants, while Earth supports life due to its unique atmosphere and magnetic field. "
                "Historical events such as the Industrial Revolution reshaped human societies, laying the groundwork for today's interconnected world. "
                "My name is Alex, and I'm fascinated by these topics. "
                "The Sun, central to our solar system, has a mass that constitutes the majority of the system.")

    # Call the class with verbose output
    try:
        attributor = ResponseAttributor(
            context=context,
            threshold=55.0,
            verbose=False
        )

        textResponse, textExplanation, attribution_results = attributor.attribute_response_to_context(response)

    except ValueError as e:
        print(f"Error: {e}")
    else:
        # Process the results as needed
        print("\nFinal Outputs:")
        print("Text Response:")
        print(textResponse)
        print("\nText Explanation:")
        print(textExplanation)
        print("\nAttribution Results:")
        for result in attribution_results:
            print(result)
