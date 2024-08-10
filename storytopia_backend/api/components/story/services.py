from .model import StoryPost, Story
from storytopia_backend.api.components.user.model import User
from datetime import datetime, timezone
from .repository import create_story, get_story_by_id
from storytopia_backend.services.llm import StoryGenerationService
from storytopia_backend.services.stable_diffusion import ImageGenerationService
from google.cloud import storage
import json
import os
from openai import OpenAI
from typing import Dict, Any

# Initialize services
story_service = StoryGenerationService(
    os.getenv("GOOGLE_CLOUD_PROJECT"),
    os.getenv("GOOGLE_CLOUD_LOCATION"),
    "gemini-1.5-pro",
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
storage_client = storage.Client()
image_service = ImageGenerationService(
    openai_client=openai_client,
    storage_client=storage_client,
    bucket_name=os.getenv("GCS_BUCKET_NAME"),
    folder_name="storytopia_images_dev",
)


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


async def generate_story_with_images(prompt: str, current_user: User) -> Story:
    """
    Generate a story based on the given prompt, create images, and return a complete Story object.
    """
    # Generate story
    story_json = await story_service.generate_story(prompt)
    story_data = json.loads(story_json)

    # Generate images based on the detailed scene descriptions
    image_urls = await image_service.generate_images(story_data["Scenes"])

    # Create a Story object
    story = Story(
        title=story_data["Title"],
        author=current_user.username,
        author_id=current_user.id,
        description=story_data["Prompt"],
        story_pages=story_data["Summaries"],
        story_images=image_urls,
        private=False,  # May want to make this configurable
        createdAt=datetime.now(timezone.utc).isoformat(),
        id="",
        likes=0,
        saves=0,
    )

    # Save the story to the database
    story_id = await create_story(story.model_dump())
    story.id = story_id

    return story
