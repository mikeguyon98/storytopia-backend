from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from storytopia_backend.api.middleware.auth import get_current_user
from storytopia_backend.api.components.user.model import User
from .repository import get_all_stories
from .model import StoryPost, Story
from .services import create_user_story, get_story, generate_story_with_images, get_recent_public_stories, like_story, save_story
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()


@router.get("/")
async def get_all_stories_endpoints():
    """
    Get all stories.
    """
    return get_all_stories()


@router.post("/story")
async def create_stories_endpoint(
    story: StoryPost, current_user: User = Depends(get_current_user)
):
    return await create_user_story(story, current_user)


@router.get("/story/{story_id}")
async def get_story_by_id_endpoint(
    story_id: str, current_user: User = Depends(get_current_user)
):
    return await get_story(story_id, current_user.id)


@router.post("/stories/like")
async def like_story_endpoint(story_id: str, current_user: User = Depends(get_current_user)):
    """
    Endpoint to like a story.

    Parameters:
        story_id (str): The ID of the story to like.
        current_user (User): The current authenticated user.

    Returns:
        dict: A message indicating the like action was successful.
    """
    await like_story(story_id, current_user.id)
    return {"message": "Story liked successfully"}


@router.post("/stories/save")
async def save_story_endpoint(story_id: str, current_user: User = Depends(get_current_user)):
    """
    Endpoint to save a story.

    Parameters:
        story_id (str): The ID of the story to save.
        current_user (User): The current authenticated user.

    Returns:
        dict: A message indicating the save action was successful.
    """
    await save_story(story_id, current_user.id)
    return {"message": "Story saved successfully"}


@router.post("/generate-story-with-images")
async def generate_story_with_images_endpoint(
    prompt: str, style: str, private: bool, current_user: User = Depends(get_current_user)
) -> Story:
    """
    Generate a story based on the given prompt, create images, and return a complete Story object.
    """
    return await generate_story_with_images(prompt, style, private, current_user)

@router.get("/explore", response_model=List[Story])
async def get_explore_stories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
) -> List[Story]:
    """
    Endpoint to retrieve the most recently created public stories for the explore page.

    Parameters:
        page (int): The page number for pagination (default: 1).
        page_size (int): The number of stories per page (default: 10).

    Returns:
        List[Story]: A paginated list of the most recent public stories.
    """
    return await get_recent_public_stories(page, page_size)
