from .model import StoryPost, Story
from storytopia_backend.api.components.user.model import User
from datetime import datetime, timezone
from .repository import create_story, get_story_by_id


async def create_user_story(story_post: StoryPost, current_user: User) -> Story:
    story_data = {
        "title": story_post.title,
        "description": story_post.description,
        "author": current_user.username,
        "author_id": current_user.id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "private": story_post.private,
        "story_pages": [],
        "story_images": [],
        "likes": 0,
        "saves": 0,
        "id": ""
    }
    story_id = await create_story(story_data)
    story_data["id"] = story_id
    return Story(**story_data)

async def get_story(story_id: str, user_id: str) -> Story:
    story_ref = await get_story_by_id(story_id)
    if story_ref is None:
        return {"message": "Story not found"}
    if story_ref.private and story_ref.author_id != user_id:
        return {"message": "Story is private"}
    return story_ref
