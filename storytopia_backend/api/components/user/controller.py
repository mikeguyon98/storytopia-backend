"""
This module defines the API routes for user-related operations.

It sets up the FastAPI router and includes a route to retrieve the current user.

Modules:
    fastapi: FastAPI framework for building APIs.
    storytopia_backend.api.middleware.auth: Middleware for authentication.
    .model: User model definition.

Functions:
    read_user: Retrieve the current user.
    update_user_endpoint: Update the current user's details.
    follow_user_endpoint: Follow a user.
    get_followers_endpoint: Get the list of followers for the current user.
    get_following_endpoint: Get the list of users the current user is following.
"""
from typing import List
from fastapi import APIRouter, Depends
from storytopia_backend.api.middleware.auth import get_current_user
from .services import (
    follow_user, get_followers, get_following, update_user_details
)
from .model import User, UserUpdate

router = APIRouter()

@router.get("/me", response_model=User)
async def read_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Retrieve the current user.
    
    Parameters:
        current_user (User): The current user object.
    
    Returns:
        User: The current user.
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_endpoint(user_update: UserUpdate, current_user: User = Depends(get_current_user)) -> User:
    """
    Endpoint to update the current user's details.

    Parameters:
        user_update (UserUpdate): The updated user information.
        current_user (User): The current authenticated user.

    Returns:
        User: The updated user object.
    """
    return await update_user_details(current_user.id, user_update)

@router.post("/follow/{user_id}", response_model=None)
async def follow_user_endpoint(user_id: str, current_user: User = Depends(get_current_user)):
    """
    Endpoint to follow a user.

    Parameters:
        user_id (str): The ID of the user to follow.
        current_user (User): The current authenticated user.

    Returns:
        dict: A message indicating the follow action was successful.
    """
    await follow_user(current_user.id, user_id)
    return {"message": "Followed user successfully"}

@router.get("/followers", response_model=List[User])
async def get_followers_endpoint(current_user: User = Depends(get_current_user)):
    """
    Endpoint to get the list of followers for the current user.

    Parameters:
        current_user (User): The current authenticated user.

    Returns:
        List[User]: A list of users who follow the current user.
    """
    return await get_followers(current_user.id)

@router.get("/following", response_model=List[User])
async def get_following_endpoint(current_user: User = Depends(get_current_user)):
    """
    Endpoint to get the list of users the current user is following.

    Parameters:
        current_user (User): The current authenticated user.

    Returns:
        List[User]: A list of users the current user is following.
    """
    return await get_following(current_user.id)
