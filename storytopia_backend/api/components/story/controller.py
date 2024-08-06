from fastapi import APIRouter, Depends
from storytopia_backend.api.middleware.auth import get_current_user
from storytopia_backend.api.components.user.model import User
from .repository import get_all_stories
from .model import StoryPost
from .services import create_user_story, get_story

router = APIRouter()

@router.get("/")
async def get_all_stories_endpoints():
    """
    Get all stories.
    """
    return get_all_stories()
    

@router.post("/story")
async def create_stories_endpoint( story: StoryPost, current_user: User = Depends(get_current_user)):
    return await create_user_story(story, current_user)

@router.get("/story/{story_id}")
async def get_story_by_id_endpoint(story_id: str, current_user: User = Depends(get_current_user)):
    print("story_id", story_id)
    print("current_user", current_user)
    return await get_story(story_id, current_user.id)