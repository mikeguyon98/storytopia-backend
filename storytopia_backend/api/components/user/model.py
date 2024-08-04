"""
This module defines the data models used in the application.

Classes:
    User: Represents a user with various attributes including username, email, 
    profile picture, bio, followers, following, and different categories of books.
"""
from typing import List
from pydantic import BaseModel

class User(BaseModel):
    """
    Represents a user with various attributes.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email of the user.
        profile_picture (str): The URL to the profile picture of the user.
        bio (str): The bio of the user.
        followers (List[str]): The list of user IDs following this user.
        following (List[str]): The list of user IDs this user is following.
        liked_books (List[str]): The list of book IDs liked by this user.
        saved_books (List[str]): The list of book IDs saved by this user.
        public_books (List[str]): The list of public book IDs created by this user.
        private_books (List[str]): The list of private book IDs created by this user.
    """
    username: str
    profile_picture: str
    bio: str
    followers: List[str] = []
    following: List[str] = []
    liked_books: List[str] = []
    saved_books: List[str] = []
    public_books: List[str] = []
    private_books: List[str] = []
    createdAt: str
