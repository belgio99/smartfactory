from typing import List, Optional, Dict, Any
from rapidfuzz import process, fuzz
import nltk
from nltk.tokenize import sent_tokenize

def attribute_response_to_documents(
    response: str,
    documents: List[str],
    threshold: float = 60.0,
    verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    Attributes segments of a response to the most similar segments in the provided documents.

    Parameters:
    - response (str): The LLM-generated response to attribute.
    - documents (List[str]): The list of documents to compare against.
    - threshold (float): The similarity score threshold (0-100). Defaults to 60.0.
    - verbose (bool): If True, prints the attribution results. Defaults to False.

    Returns:
    - attribution (List[Dict[str, Any]]): A list of dictionaries containing attribution results.

    Raises:
    - ValueError: If inputs are not of the expected types or formats.
    """
    # Input validation
    if not isinstance(response, str):
        raise ValueError(f"The 'response' parameter must be a string. Received type {type(response).__name__}.")

    if not isinstance(documents, list):
        raise ValueError(f"The 'documents' parameter must be a list of strings. Received type {type(documents).__name__}.")
    else:
        for i, doc in enumerate(documents):
            if not isinstance(doc, str):
                raise ValueError(f"All items in the 'documents' list must be strings. Item at index {i} is of type {type(doc).__name__}.")

    if not isinstance(threshold, (int, float)):
        raise ValueError(f"The 'threshold' parameter must be a number (int or float). Received type {type(threshold).__name__}.")
    elif not (0 <= threshold <= 100):
        raise ValueError(f"The 'threshold' parameter must be between 0 and 100. Received {threshold}.")

    if not isinstance(verbose, bool):
        raise ValueError(f"The 'verbose' parameter must be a boolean. Received type {type(verbose).__name__}.")

    # Ensure NLTK 'punkt' tokenizer is downloaded
    nltk.download('punkt', quiet=True)

    # Step 1: Segment the response into sentences
    response_segments = sent_tokenize(response)
    if not response_segments:
        raise ValueError("The 'response' parameter does not contain any sentences after tokenization.")

    # Step 2: Segment the documents into sentences
    document_segments = []
    for idx, doc in enumerate(documents):
        doc_sentences = sent_tokenize(doc)
        if not doc_sentences:
            raise ValueError(f"The document at index {idx} does not contain any sentences after tokenization.")
        document_segments.extend(doc_sentences)

    if not document_segments:
        raise ValueError("No document sentences found after tokenization.")

    # Step 3: Compare each response segment with all document segments
    attribution = []
    for response_segment in response_segments:
        # Use RapidFuzz to find the best match for the response segment
        match = process.extractOne(
            response_segment, document_segments, scorer=fuzz.token_set_ratio
        )

        # Handle cases where no match is found
        if match:
            best_match, similarity_score, _ = match
        else:
            best_match, similarity_score = None, 0

        # Proceed only if similarity score meets or exceeds the threshold
        if similarity_score >= threshold and best_match is not None:
            result = {
                "response_segment": response_segment,
                "document": best_match,
                "similarity_score": similarity_score
            }
        else:
            result = {
                "response_segment": response_segment,
                "document": None,
                "similarity_score": similarity_score
            }
        attribution.append(result)

        # Verbose output
        if verbose:
            print(f"Response Segment: {result['response_segment']}")
            if result['document']:
                print(f"Attributed Document: {result['document']}")
                print(f"Similarity Score: {result['similarity_score']:.2f}%")
            else:
                print("No document meets the similarity threshold.")
                print(f"Highest Similarity Score: {result['similarity_score']:.2f}%")
            print("-" * 50)

    return attribution

if __name__ == "__main__":

    # Example documents and response
    documents = [
        "The sky is blue and often has clouds. Grass is green and is found in gardens and parks.",
        "The sun is a star located at the center of our solar system."
    ]

    response = "The sun is at the center of the solar system. The grass is green in parks. My name is Jeff"

    # Call the function with verbose output
    try:
        attribution_results = attribute_response_to_documents(
            response=response,
            documents=documents,
            threshold=60.0,
            verbose=True
        )
    except ValueError as e:
        print(f"Error: {e}")
    else:
        # Process the results as needed
        print("Attribution Results:")
        for result in attribution_results:
            print(result)