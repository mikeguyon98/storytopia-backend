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
from storytopia_backend.api.components.story.repository import get_story_by_id
from storytopia_backend.api.components.story.model import Story
from .model import User, UserUpdate
from .repository import get_user_by_id, update_user

async def update_user_details(user_id: str, user_update: UserUpdate) -> User:
    """
    Update user details.

    Parameters:
        user_id (str): The ID of the user to update.
        user_update (UserUpdate): The updated user information.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_id(user_id)
    for key, value in user_update.model_dump().items():
        if value:
            setattr(user, key, value)
    await update_user(user)
    return user

async def follow_user(current_user_id: str, follow_user_id: str) -> None:
    """
    Follow a user.

    Parameters:
        current_user_id (str): The ID of the current user.
        follow_user_id (str): The ID of the user to follow.

    Returns:
        None
    """
    current_user = await get_user_by_id(current_user_id)
    user_to_follow = await get_user_by_id(follow_user_id)
    if follow_user_id not in current_user.following:
        current_user.following.append(follow_user_id)
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

