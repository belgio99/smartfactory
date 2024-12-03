from pydantic import BaseModel

class Question(BaseModel):
  text: str

class Answer(BaseModel):
  text: str