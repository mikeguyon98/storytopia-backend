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
from fastapi import APIRouter, Depends, HTTPException
from storytopia_backend.api.middleware.auth import get_current_user
from .services import (
    follow_user,
    unfollow_user,
    get_followers,
    get_following,
    update_user_details,
    get_user_stories,
    get_user_public_stories,
    get_public_user_info,
    is_following_user,
)
from .model import User, UserUpdate
from storytopia_backend.api.components.story.model import Story

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
async def update_user_endpoint(
    user_update: UserUpdate, current_user: User = Depends(get_current_user)
) -> User:
    """
    Endpoint to update the current user's details.

    Parameters:
        user_update (UserUpdate): The updated user information.
        current_user (User): The current authenticated user.

    Returns:
        User: The updated user object.
    """
    return await update_user_details(current_user.id, user_update)


@router.post("/follow/{username}", response_model=None)
async def follow_user_endpoint(
    username: str, current_user: User = Depends(get_current_user)
):
    """
    Endpoint to follow a user.

    Parameters:
        user_id (str): The ID of the user to follow.
        current_user (User): The current authenticated user.

    Returns:
        dict: A message indicating the follow action was successful.
    """
    await follow_user(current_user.id, username)
    return {"message": "Followed user successfully"}


@router.post("/unfollow/{username}", response_model=dict)
async def unfollow_user_endpoint(
    username: str, current_user: User = Depends(get_current_user)
):
    """
    Endpoint to unfollow a user.

    Parameters:
        username (str): The name of the user to unfollow.
        current_user (User): The current authenticated user.

    Returns:
        dict: A message indicating the unfollow action was successful.
    """
    await unfollow_user(current_user.id, username)
    return {"message": "Unfollowed user successfully"}


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


@router.get("/me/public_posts", response_model=List[Story])
async def get_public_posts(
    current_user: User = Depends(get_current_user),
) -> List[Story]:
    """
    Endpoint to retrieve the current user's public posts.

    Parameters:
        current_user (User): The current authenticated user.

    Returns:
        List[Story]: A list of public stories created by the user.
    """
    print(current_user)
    return await get_user_stories(current_user.public_books)


@router.get("/me/private_posts", response_model=List[Story])
async def get_private_posts(
    current_user: User = Depends(get_current_user),
) -> List[Story]:
    """
    Endpoint to retrieve the current user's private posts.

    Parameters:
        current_user (User): The current authenticated user.

    Returns:
        List[Story]: A list of private stories created by the user.
    """
    return await get_user_stories(current_user.private_books)


@router.get("/me/saved_posts", response_model=List[Story])
async def get_saved_posts(
    current_user: User = Depends(get_current_user),
) -> List[Story]:
    """
    Endpoint to retrieve the current user's saved posts.

    Parameters:
        current_user (User): The current authenticated user.

    Returns:
        List[Story]: A list of saved stories saved by the user.
    """
    return await get_user_public_stories(current_user.saved_books)


@router.get("/me/liked_posts", response_model=List[Story])
async def get_liked_posts(
    current_user: User = Depends(get_current_user),
) -> List[Story]:
    """
    Endpoint to retrieve the current user's liked posts.

    Parameters:
        current_user (User): The current authenticated user.

    Returns:
        List[Story]: A list of liked stories liked by the user.
    """
    return await get_user_public_stories(current_user.liked_books)


@router.get("/username/{username}", response_model=dict)
async def get_public_info_by_username(
    username: str, current_user: User = Depends(get_current_user)
):
    """
    Endpoint to get public information for a user by username.

    Parameters:
        username (str): The username of the user to fetch.
        current_user (User): The current authenticated user.

    Returns:
        Dict: A dictionary containing public user information.
    """
    user_info = await get_public_user_info(username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info


@router.get("/is-following/{username}", response_model=dict)
async def is_following_user_endpoint(
    username: str, current_user: User = Depends(get_current_user)
) -> dict:
    """
    Check if the current user is following another user.

    Parameters:
        username (str): The username of the user to check.
        current_user (User): The current authenticated user.

    Returns:
        dict: A dictionary containing a boolean indicating if the current user is following the specified user.
    """
    is_following = await is_following_user(current_user.id, username)
    return {"is_following": is_following}
