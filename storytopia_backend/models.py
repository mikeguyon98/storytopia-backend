"""
This module defines the data models used in the application.

Classes:
    User: Represents a user with a username and creation date.
"""
from pydantic import BaseModel

class User(BaseModel):
    """
    Represents a user with a username and creation date.

    Attributes:
        username (str): The username of the user.
        createdAt (str): The date and time when the user was created.
    """
    username: str
    createdAt: str
