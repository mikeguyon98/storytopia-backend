"""
This module provides repository functions for interacting with the user data in Firestore.

It includes functions to retrieve a user by their ID and update a user's information.

Modules:
    storytopia_backend.firebase_config: Configuration for Firebase.
    .model: User model definition.

Functions:
    get_user_by_id: Retrieve a user by their ID.
    update_user: Update a user's information in the database.
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
    user_ref = db.collection('users').document(user_id)
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
    user_ref = db.collection('users').document(user.id)
    user_ref.set(user.dict())
