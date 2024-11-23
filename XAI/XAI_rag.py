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
    ref_num = 1
    textResponse = ''
    textExplanation = ''

    # Step 4: Compare each response segment with all context segments
    for response_segment in response_segments:
        # Use RapidFuzz to find the best match for the response segment
        match = process.extractOne(
            response_segment, context_segments, scorer=fuzz.token_set_ratio
        )

        # Initialize default values
        best_match = None
        similarity_score = 0

        # If a match is found, unpack the values
        if match:
            best_match, similarity_score, _ = match

        # Decide whether to attribute the context based on the similarity score
        context_match = best_match if similarity_score >= threshold else None

        # Prepare the result dictionary
        result = {
            "response_segment": response_segment,
            "context": context_match,
            "similarity_score": similarity_score
        }

        # Append the result to the attribution list
        attribution.append(result)

        # Build textResponse and textExplanation during the loop
        if context_match is not None:
            # Add reference number to response segment
            textResponse += response_segment + f'[{ref_num}] '
            # Add reference to textExplanation
            textExplanation += f'[{ref_num}] {context_match}\n'
            ref_num += 1
        else:
            textResponse += response_segment + ' '

        # Verbose output
        if verbose:
            _print_verbose(result, textResponse.strip(), textExplanation.strip())

    # Remove trailing whitespace
    textResponse = textResponse.strip()
    textExplanation = textExplanation.strip()

    return textResponse, textExplanation, attribution

if __name__ == "__main__":

    # Example context and response
    context = [
        "The sky is blue and often has clouds. Grass is green and is found in gardens and parks.",
        "The sun is a star located at the center of our solar system."
    ]

    response = "The sun is at the center of the solar system. The grass is green in parks. My name is Jeff"

    # Call the function with verbose output
    try:
        textResponse, textExplanation, attribution_results = attribute_response_to_context(
            response=response,
            context=context,
            threshold=60.0,
            verbose=True
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