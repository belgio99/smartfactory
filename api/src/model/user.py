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
        role (str): The role of the user.
        site (str): The site of the user.
    """
    username: str
    email: str
    role: str
    password: str
    site: str

class ChangePassword(BaseModel):
    """
    Represents the register request body.

    Attributes:
        old_password (str): The old password of the user.
        new_password (str): The new password of the user.
    """
    old_password: str
    new_password: str


class UserInfo(BaseModel):
    """
    Represents a user.

    Attributes:
        userId (str): The id of the user (None in case of registration).
        username (str): The username of the user.
        email (str): The email of the user.
        access_token (str): The access token for the user.
        role (str): The role of the user.
        site (str): The site of the user.
    """
    userId: int
    username: str
    email: str
    access_token: str
    role: str
    site: str

    def to_dict(self):
        """
        Convert the UserInfo object to a dictionary.

        Returns:
            dict: A dictionary representation of the UserInfo object.
        """
        return {
            "userId": self.userId,
            "username": self.username,
            "email": self.email,
            "access_token": self.access_token,
            "role": self.role,
            "site": self.site
        }