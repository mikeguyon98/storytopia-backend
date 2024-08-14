"""
This module provides services for user-related operations such as following users 
and retrieving followers.

It includes functions to follow a user, get the list of followers for a user, and 
get the list of users a user is following.

Modules:
    typing: Provides support for type hints.
    .model: User model definition.
    .repository: Functions to interact with the user data in Firestore.

Functions:
    follow_user: Follow a user.
    get_followers: Get the list of followers for a user.
    get_following: Get the list of users a user is following.
    update_user_details: Update user details.
"""

from typing import List
from fastapi import HTTPException
from storytopia_backend.api.components.story.repository import get_story_by_id
from storytopia_backend.api.components.story.model import Story
from .model import User, UserUpdate
from .repository import (
    get_user_by_id,
    update_user,
    check_username_exists,
    get_user_by_username,
)


async def update_user_details(user_id: str, user_update: UserUpdate) -> User:
    """
    Update user details.

    Parameters:
    user_id (str): The ID of the user to update.
    user_update (UserUpdate): The updated user information.

    Returns:
    User: The updated user object.

    Raises:
    HTTPException: If the username already exists for another user.
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if username is being updated
    if user_update.username and user_update.username != user.username:
        # Check if the new username already exists
        username_exists = await check_username_exists(user_update.username)
        if username_exists:
            raise HTTPException(status_code=400, detail="Username already exists")

    for key, value in user_update.model_dump().items():
        if value is not None:
            setattr(user, key, value)

    await update_user(user)
    return user


async def follow_user(current_user_id: str, follow_username: str) -> None:
    """
    Follow a user.

    Parameters:
        current_user_id (str): The ID of the current user.
        follow_username (str): The username of the user to follow.

    Returns:
        None
    """
    current_user = await get_user_by_id(current_user_id)
    user_to_follow = await get_user_by_username(follow_username)
    if user_to_follow.id not in current_user.following:
        current_user.following.append(user_to_follow.id)
        user_to_follow.followers.append(current_user_id)
        await update_user(current_user)
        await update_user(user_to_follow)


async def get_followers(user_id: str) -> List[User]:
    """
    Get the list of followers for a user.

    Parameters:
        user_id (str): The ID of the user.

    Returns:
        List[User]: A list of users who follow the specified user.
    """
    user = await get_user_by_id(user_id)
    return [await get_user_by_id(follower_id) for follower_id in user.followers]


async def get_following(user_id: str) -> List[User]:
    """
    Get the list of users the specified user is following.

    Parameters:
        user_id (str): The ID of the user.

    Returns:
        List[User]: A list of users the specified user is following.
    """
    user = await get_user_by_id(user_id)
    return [await get_user_by_id(following_id) for following_id in user.following]


async def get_user_stories(story_ids: List[str]) -> List[Story]:
    """
    Retrieve a list of stories based on the provided story IDs.

    Parameters:
        story_ids (List[str]): The list of story IDs to retrieve.

    Returns:
        List[Story]: A list of story objects.
    """
    return [await get_story_by_id(story_id) for story_id in story_ids]


async def get_user_public_stories(story_ids: List[str]) -> List[Story]:
    """
    Retrieve a list of stories based on the provided story IDs,
    filtering out stories that are marked as private.

    Parameters:
        story_ids (List[str]): The list of story IDs to retrieve.

    Returns:
        List[Story]: A list of non-private story objects.
    """
    stories = [await get_story_by_id(story_id) for story_id in story_ids]
    return [story for story in stories if not story.private]


async def get_public_user_info(username: str) -> dict:
    """
    Get public information for a user.

    Parameters:
        username (str): The username of the user.

    Returns:
        Dict: A dictionary containing public user information.
    """
    user = await get_user_by_username(username)
    if not user:
        return None
    return {
        "username": user.username,
        "profile_picture": user.profile_picture,
        "bio": user.bio,
        "public_books": user.public_books,
    }


async def unfollow_user(current_user_id: str, username: str) -> None:
    """
    Unfollow a user.

    Parameters:
        current_user_id (str): The ID of the current user.
        username (str): The username of the user to unfollow.

    Returns:
        None
    """
    current_user = await get_user_by_id(current_user_id)
    user_to_unfollow = await get_user_by_username(username)

    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User to unfollow not found")

    if user_to_unfollow.id in current_user.following:
        current_user.following.remove(user_to_unfollow.id)
        user_to_unfollow.followers.remove(current_user_id)
        await update_user(current_user)
        await update_user(user_to_unfollow)
    else:
        raise HTTPException(status_code=400, detail="You are not following this user")


async def is_following_user(current_user_id: str, username: str) -> bool:
    """
    Check if a user is following another user.

    Parameters:
        current_user_id (str): The ID of the current user.
        username (str): The username of the user to check.

    Returns:
        bool: True if the current user is following the specified user, False otherwise.

    Raises:
        HTTPException: If the user to check is not found.
    """
    current_user = await get_user_by_id(current_user_id)
    user_to_check = await get_user_by_username(username)

    if not user_to_check:
        raise HTTPException(status_code=404, detail="User not found")

    return user_to_check.id in current_user.following
