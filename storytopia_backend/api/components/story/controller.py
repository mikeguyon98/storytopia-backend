from fastapi import APIRouter, Depends, HTTPException
from storytopia_backend.api.middleware.auth import get_current_user
from storytopia_backend.api.components.user.model import User
from .repository import get_all_stories
from .model import StoryPost, Story
from .services import create_user_story, get_story, generate_story_with_images
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


@router.post("/generate-story-with-images")
async def generate_story_with_images_endpoint(
    prompt: str, current_user: User = Depends(get_current_user)
) -> Story:
    """
    Generate a story based on the given prompt, create images, and return a complete Story object.
    """
    return await generate_story_with_images(prompt, current_user)
