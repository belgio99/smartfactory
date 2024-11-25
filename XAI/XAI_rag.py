from typing import List, Dict, Any, Tuple
from rapidfuzz import process, fuzz
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK 'punkt' tokenizer is downloaded upon module import
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


def _print_verbose(result, textResponse, textExplanation):
    print(f"Response Segment: {result['response_segment']}")
    if result['context']:
        print(f"Attributed Context: {result['context']}")
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


def _validate_inputs(response, context, threshold, verbose):
    """
    Validates the inputs to the attribute_response_to_context function.

    Raises:
        ValueError: If any of the inputs are invalid.
    """
    if not isinstance(response, str):
        raise ValueError(f"The 'response' parameter must be a string. Received type {type(response).__name__}.")

    if not isinstance(context, list):
        raise ValueError(f"The 'context' parameter must be a list of strings. Received type {type(context).__name__}.")
    else:
        for i, ctx in enumerate(context):
            if not isinstance(ctx, str):
                raise ValueError(f"All items in the 'context' list must be strings. Item at index {i} is of type {type(ctx).__name__}.")

    if not isinstance(threshold, (int, float)):
        raise ValueError(f"The 'threshold' parameter must be a number (int or float). Received type {type(threshold).__name__}.")
    elif not (0 <= threshold <= 100):
        raise ValueError(f"The 'threshold' parameter must be between 0 and 100. Received {threshold}.")

    if not isinstance(verbose, bool):
        raise ValueError(f"The 'verbose' parameter must be a boolean. Received type {type(verbose).__name__}.")


def attribute_response_to_context(
    response: str,
    context: List[str],
    threshold: float = 60.0,
    verbose: bool = False
) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Attributes segments of a response to the most similar segments in the provided context.

    Parameters:
    - response (str): The LLM-generated response to attribute.
    - context (List[str]): The list of context strings to compare against.
    - threshold (float): The similarity score threshold (0-100). Defaults to 60.0.
    - verbose (bool): If True, prints the attribution results. Defaults to False.

    Returns:
    - A tuple containing:
        - textResponse (str): The response with reference numbers added.
        - textExplanation (str): The references with corresponding numbers.
        - attribution (List[Dict[str, Any]]): A list of dictionaries containing attribution results.

    Raises:
    - ValueError: If inputs are not of the expected types or formats.
    """
    # Input validation
    _validate_inputs(response, context, threshold, verbose)

    # Step 1: Segment the response into sentences
    response_segments = sent_tokenize(response)
    if not response_segments:
        raise ValueError("The 'response' parameter does not contain any sentences after tokenization.")

    # Step 2: Segment the context into sentences
    context_segments = []
    for idx, ctx in enumerate(context):
        ctx_sentences = sent_tokenize(ctx)
        if not ctx_sentences:
            raise ValueError(f"The context at index {idx} does not contain any sentences after tokenization.")
        context_segments.extend(ctx_sentences)

    if not context_segments:
        raise ValueError("No context sentences found after tokenization.")

    # Step 3: Initialize variables
    attribution = []
    references = []
    textResponse = ''
    textExplanation = ''

    # Step 4: Compare each response segment with all context segments
    for response_segment in response_segments:
        # Use RapidFuzz to find the best match for the response segment
        match = process.extractOne(
            response_segment, context_segments, scorer=fuzz.token_set_ratio, score_cutoff=threshold
        )

        # Initialize default values
        context_match = None
        similarity_score = 0

        # If a match is found, unpack the values and build textResponse and textExplanation during the loop
        if match:
            context_match, similarity_score, _ = match
            if context_match not in references:
                # Add reference to textExplanation
                references.append(context_match)
                textExplanation += f'[{len(references)}] {context_match}\n'
            # Add reference number to response segment
            ref_num = references.index(context_match) + 1
            textResponse += response_segment + f'[{ref_num}] '
        else:
            textResponse += response_segment + ' '

        # Prepare the result dictionary
        result = {
            "response_segment": response_segment,
            "context": context_match,
            "similarity_score": similarity_score
        }

        # Append the result to the attribution list
        attribution.append(result)

        # Verbose output
        if verbose:
            _print_verbose(result, textResponse.strip(), textExplanation.strip())

    # Remove trailing whitespace
    textResponse = textResponse.strip()
    textExplanation = textExplanation.strip()

    return textResponse, textExplanation, attribution

if __name__ == "__main__":

    # Example context and response with large text
    context = [
        "The solar system consists of the Sun and the celestial objects that are gravitationally bound to it.",
        "This includes eight planets, their moons, dwarf planets, and countless asteroids and comets.",
        "The Sun, a G-type main-sequence star, accounts for 99.86% of the solar system's mass.",
        "It is the central body around which all planets orbit.",
        "The inner planets, Mercury, Venus, Earth, and Mars, are terrestrial planets with rocky surfaces.",
        "The outer planets, Jupiter, Saturn, Uranus, and Neptune, are gas and ice giants.",
        "The Earth's atmosphere is composed of 78% nitrogen, 21% oxygen, and trace amounts of other gases such as argon and carbon dioxide.",
        "It provides the air we breathe and protects us from harmful solar radiation.",
        "The ozone layer, part of the Earth's stratosphere, absorbs the majority of the Sun's ultraviolet radiation.",
        "Earth's surface is mostly covered by water. It is the only known planet to support life.",
        "Its magnetic field shields it from the solar wind, preserving its atmosphere and enabling diverse ecosystems.",
        "Artificial intelligence (AI) has rapidly advanced in recent years.",
        "It is impacting various industries including healthcare, finance, and transportation.",
        "Machine learning, a subset of AI, focuses on developing algorithms that allow computers to learn from data without being explicitly programmed.",
        "Deep learning, a specialized form of machine learning, utilizes artificial neural networks to process complex data and achieve remarkable results.",
        "It excels in fields like natural language processing and image recognition.",
        "Ethical considerations in AI development, such as bias and privacy, remain critical concerns.",
        "The history of human civilization spans thousands of years.",
        "It is marked by the development of writing, agriculture, and industry.",
        "Ancient civilizations like Mesopotamia, Egypt, and the Indus Valley contributed to the foundations of modern society.",
        "They introduced systems of governance, trade, and cultural exchange.",
        "The Industrial Revolution, beginning in the late 18th century, transformed economies and societies.",
        "It ushered in an era of rapid technological progress. Today, globalization connects the world more than ever.",
        "It enables unprecedented collaboration and exchange."
    ]

    response = "Artificial intelligence has revolutionized industries by improving processes in fields like transportation and healthcare. For instance, machine learning allows systems to adapt and learn without being explicitly programmed. The Earth's atmosphere is vital for life, with nitrogen and oxygen making up its majority. The Sun, central to our solar system, has a mass that constitutes the majority of the system. Planets like Jupiter and Saturn are gas giants, while Earth supports life due to its unique atmosphere and magnetic field. Historical events such as the Industrial Revolution reshaped human societies, laying the groundwork for today's interconnected world. My name is Alex, and I'm fascinated by these topics. The Sun, central to our solar system, has a mass that constitutes the majority of the system."

    # Call the function with verbose output
    try:
        textResponse, textExplanation, attribution_results = attribute_response_to_context(
            response=response,
            context=context,
            threshold=55.0,
            verbose=False
        )
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