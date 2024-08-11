from typing import List
from .model import StoryPost, Story
from storytopia_backend.api.components.user.model import User
from datetime import datetime, timezone
from .repository import create_story, get_story_by_id, get_recent_public_stories_from_db
from storytopia_backend.services.llm import StoryGenerationService
from storytopia_backend.services.stable_diffusion import ImageGenerationService
from storytopia_backend.api.components.user.repository import update_user
from google.cloud import storage
from storytopia_backend.api.components.story import image_service, story_service
import json
from dotenv import load_dotenv

load_dotenv()


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
        "id": "",
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


async def generate_story_with_images(
    prompt: str, style: str, private: bool, current_user: User,
) -> Story:
    """
    Generate a story based on the given prompt, create images, and return a complete Story object.
    """
    # Generate story
    story_json = await story_service.generate_story(prompt)
    story_data = json.loads(story_json)

    # Generate images based on the detailed scene descriptions
    image_urls = await image_service.generate_images(story_data["Scenes"], style)

    # Create a Story object
    story = Story(
        title=story_data["Title"],
        author=current_user.username,
        author_id=current_user.id,
        description=story_data["Prompt"],
        story_pages=story_data["Summaries"],
        story_images=image_urls,
        private=private,  # May want to make this configurable
        createdAt=datetime.now(timezone.utc).isoformat(),
        id="",
        likes=0,
        saves=0,
    )

    # Save the story to the database
    story_id = await create_story(story.model_dump())
    story.id = story_id

    if private:
        current_user.private_books.append(story_id)
    else:
        current_user.public_books.append(story_id)

    await update_user(current_user)

    return story

async def get_recent_public_stories(page: int, page_size: int) -> List[Story]:
    """
    Retrieve the most recently created public stories for the explore page.

    Parameters:
        page (int): The page number for pagination.
        page_size (int): The number of stories per page.

    Returns:
        List[Story]: A paginated list of the most recent public stories.
    """
    skip = (page - 1) * page_size
    return await get_recent_public_stories_from_db(skip, page_size)

