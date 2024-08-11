"""
This module provides repository functions for interacting with the user data in Firestore.
It includes functions to retrieve a user by their ID, update a user's information, and check if a username exists.

Modules:
    storytopia_backend.firebase_config: Configuration for Firebase.
    .model: User model definition.

Functions:
    get_user_by_id: Retrieve a user by their ID.
    update_user: Update a user's information in the database.
    check_username_exists: Check if a username already exists in the database.
"""

from storytopia_backend.firebase_config import db
from .model import User


async def get_user_by_id(user_id: str) -> User:
    """
    Retrieve a user by their ID.

    Parameters:
    user_id (str): The ID of the user to retrieve.

    Returns:
    User: The user object if found, otherwise None.
    """
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    return User(**user_doc.to_dict()) if user_doc.exists else None


async def update_user(user: User) -> None:
    """
    Update a user's information in the database.

    Parameters:
    user (User): The user object containing updated information.

    Returns:
    None
    """
    user_ref = db.collection("users").document(user.id)
    user_ref.set(user.dict())


async def check_username_exists(username: str) -> bool:
    """
    Check if a username already exists in the database.

    Parameters:
    username (str): The username to check.

    Returns:
    bool: True if the username exists, False otherwise.
    """
    users_ref = db.collection("users")
    query = users_ref.where("username", "==", username).limit(1)
    docs = query.get()
    return len(docs) > 0
