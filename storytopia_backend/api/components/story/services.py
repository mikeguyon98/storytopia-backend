from typing import List
from .model import StoryPost, Story
from storytopia_backend.api.components.user.model import User
from datetime import datetime, timezone
from .repository import (
    create_story,
    get_story_by_id,
    get_recent_public_stories_from_db,
    update_story,
    send_story_generation_email,
)
from storytopia_backend.services.llm import StoryGenerationService
from storytopia_backend.services.stable_diffusion import ImageGenerationService
from storytopia_backend.api.components.user.repository import (
    update_user,
    get_user_by_id,
)
from google.cloud import storage
from storytopia_backend.api.components.story import (
    image_service,
    story_service,
)
import json
from google.cloud import texttospeech
import asyncio
from dotenv import load_dotenv
from storytopia_backend.firebase_config import db
import uuid
from fastapi import BackgroundTasks
import os

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

load_dotenv()


async def save_speech_to_storage(audio_content: bytes) -> str:
    # Initialize the Google Cloud Storage client
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)

    folder = 'storytopia_audio_dev'

    # Create a unique file name for each audio file
    file_name = f"{folder}/{uuid.uuid4()}.mp3"

    # Create a blob (file) in the bucket
    blob = bucket.blob(file_name)

    # Upload the audio content to the blob
    blob.upload_from_string(audio_content, content_type='audio/mpeg')

    # Make the blob publicly accessible (optional)
    blob.make_public()

    # Return the public URL
    return blob.public_url


async def generate_speech_for_page(text: str) -> str:
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config)

    # Save the audio content and return the public URL
    return await save_speech_to_storage(response.audio_content)


async def generate_audio_files(story: Story):
    if story.audio_files:
        print(f"Audio files already exist for story ID: {story.id}")
        return
    try:
        urls = await asyncio.gather(*[generate_speech_for_page(page) for page in story.story_pages])
        story.audio_files = urls
        await update_story(story)
    except Exception as e:
        print(f"Error generating audio files: {e}")


async def create_user_story(story_post: StoryPost, current_user: User, background_tasks: BackgroundTasks) -> Story:
    story_data = {
        "audio_files": [],
        "title": story_post.title,
        "description": story_post.description,
        "author": current_user.username,
        "author_id": current_user.id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "private": story_post.private,
        "story_pages": [],
        "story_images": [],
        "likes": [],
        "saves": [],
        "id": "",
    }
    story_id = await create_story(story_data)
    story_data["id"] = story_id
    story = Story(**story_data)

    background_tasks.add_task(generate_audio_files, story)

    return story


async def get_story(story_id: str, user_id: str) -> Story:
    story_ref = await get_story_by_id(story_id)
    if story_ref is None:
        return {"message": "Story not found"}
    if story_ref.private and story_ref.author_id != user_id:
        return {"message": "Story is private"}
    return story_ref


async def generate_story_with_images(
    prompt: str,
    style: str,
    private: bool,
    current_user: User,
    disability: str = None,
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
        private=private,
        createdAt=datetime.now(timezone.utc).isoformat(),
        id="",
        likes=[],
        saves=[],
        audio_files=[],
    )

    # Save the story to the database
    story_id = await create_story(story.model_dump())
    story.id = story_id

    if private:
        current_user.private_books.append(story_id)
    else:
        current_user.public_books.append(story_id)

    await update_user(current_user)
    urls = await asyncio.gather(*[generate_speech_for_page(page) for page in story.story_pages])
    story.audio_files = urls
    await update_story(story)

    # Send email notification
    await send_story_generation_email(current_user.id, story.description)

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


async def like_story(story_id: str, user_id: str) -> None:
    """
    Like a story and update the user's liked_books array.

    Parameters:
        story_id (str): The ID of the story to like.
        user_id (str): The ID of the user liking the story.

    Returns:
        None
    """
    story = await get_story_by_id(story_id)
    user = await get_user_by_id(user_id)

    if user_id not in story.likes:
        story.likes.append(user_id)
        user.liked_books.append(story_id)
        await update_story(story)
        await update_user(user)


async def unlike_story(story_id: str, user_id: str) -> None:
    """
    Unlike a story and update the user's liked_books array.

    Parameters:
        story_id (str): The ID of the story to unlike.
        user_id (str): The ID of the user unliking the story.

    Returns:
        None
    """
    story = await get_story_by_id(story_id)
    user = await get_user_by_id(user_id)

    if user_id in story.likes:
        story.likes.remove(user_id)
        user.liked_books.remove(story_id)
        await update_story(story)
        await update_user(user)


async def save_story(story_id: str, user_id: str) -> None:
    """
    Save a story and update the user's saved_books array.

    Parameters:
        story_id (str): The ID of the story to save.
        user_id (str): The ID of the user saving the story.

    Returns:
        None
    """
    story = await get_story_by_id(story_id)
    user = await get_user_by_id(user_id)

    if user_id not in story.saves:
        story.saves.append(user_id)
        user.saved_books.append(story_id)
        await update_story(story)
        await update_user(user)


async def unsave_story(story_id: str, user_id: str) -> None:
    """
    Unsave a story and update the user's saved_books array.

    Parameters:
        story_id (str): The ID of the story to unsave.
        user_id (str): The ID of the user unsaving the story.

    Returns:
        None
    """
    story = await get_story_by_id(story_id)
    user = await get_user_by_id(user_id)

    if user_id in story.saves:
        story.saves.remove(user_id)
        user.saved_books.remove(story_id)
        await update_story(story)
        await update_user(user)


async def toggle_story_privacy(story_id: str, user_id: str) -> Story:
    """
    Toggle the privacy setting of a story and update the user's book lists.

    Parameters:
        story_id (str): The ID of the story to toggle.
        user_id (str): The ID of the user who owns the story.

    Returns:
        Story: The updated Story object.
    """
    story = await get_story_by_id(story_id)
    user = await get_user_by_id(user_id)

    if story.author_id != user_id:
        raise ValueError("User does not have permission to modify this story")

    # Toggle the privacy setting
    story.private = not story.private

    # Update the user's book lists
    if story.private:
        if story_id in user.public_books:
            user.public_books.remove(story_id)
        if story_id not in user.private_books:
            user.private_books.append(story_id)
    else:
        if story_id in user.private_books:
            user.private_books.remove(story_id)
        if story_id not in user.public_books:
            user.public_books.append(story_id)

    # Update both the story and the user in the database
    await update_story(story)
    await update_user(user)

    return story
