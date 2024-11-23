from pydantic import BaseModel
from typing import Union

class Login(BaseModel):
    """
    Represents the login request body.

    Attributes:
        user (str): The login username/email.
        isEmail (bool): Indicates if the "user" parameter represents the username or the email of the user logging in.
        password (str): The password of the user.
    """
    user: str
    isEmail: bool
    password: str

class Register(BaseModel):
    """
    Represents the register request body.

    Attributes:
        username (str): The username of the user.
        email (str): The email of the user.
        password (str): The password of the user.
        type (str): The type of the user.
    """
    username: str
    email: str
    role: str
    password: str
    sitename: str
    type: str

class UserInfo(BaseModel):
    """
    Represents a user.

    Attributes:
        userId (str): The id of the user (None in case of registration).
        username (str): The username of the user.
        email (str): The email of the user.
        type (str): The type of the user.
    """
    userId: int
    username: str
    email: str
    access_token: str
    type: str