from typing import Optional
from pydantic import BaseModel

class Question(BaseModel):
    """
    Represents a user's input question.

    Attributes:
        userInput (str): The input question.
        userId (str): The userId requesting the question.
    """
    userInput: str
    userId: str


class Answer(BaseModel):
    """
    Represents the response to a user's question, including the answer and explanation.

    Attributes:
        textResponse (str): The response text.
        textExplanation (str): The explanation for the response.
        data (Optional[str]): Any additional data related to the response, defaults to an empty string.
        label (Optional[str]): The label of the response.
    """
    textResponse: str
    textExplanation: str
    data: Optional[str] = ''
    label: Optional[str] = 'Error'
