from typing import List
from .model import StoryPost, Story
from storytopia_backend.api.components.user.model import User
from datetime import datetime, timezone
from .repository import (
    create_story,
    get_story_by_id,
    get_recent_public_stories_from_db,
    update_story,
)

from storytopia_backend.services.llm import StoryGenerationService
from storytopia_backend.services.stable_diffusion import ImageGenerationService
from storytopia_backend.api.components.user.repository import (
    update_user,
    get_user_by_id,
)
from storytopia_backend.firebase_config import db
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
    prompt: str,
    style: str,
    private: bool,
    current_user: User,
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


async def generate_story_with_images_background(
    story_id: str,
    prompt: str,
    style: str,
    private: bool,
    current_user: User,
) -> None:
    """
    Generate a story and images in the background, updating the story object as it progresses.
    """
    try:
        # Retrieve the story
        story = await get_story_by_id(story_id)

        # Generate story
        story_json = await story_service.generate_story(prompt)
        story_data = json.loads(story_json)

        # Update story with generated content
        story.title = story_data["Title"]
        story.story_pages = story_data["Summaries"]
        story.description = f"Generating images for: {prompt}"
        await update_story(story)

        # Generate images based on the detailed scene descriptions
        image_urls = await image_service.generate_images(story_data["Scenes"], style)

        # Update story with generated images
        story.story_images = image_urls
        story.description = prompt  # Set back to original prompt
        await update_story(story)

        # Update user's books
        if private:
            current_user.private_books.append(story_id)
        else:
            current_user.public_books.append(story_id)
        await update_user(current_user)

        # Send email notification
        await send_story_completion_email(current_user.email, story.title, story.id)

    except Exception as e:
        # If an error occurs, update the story description
        story = await get_story_by_id(story_id)
        story.description += f" Error: {str(e)}"
        await update_story(story)


async def send_story_completion_email(user_email: str, story_title: str, story_id: str):
    """
    Send an email notification about story completion using Firebase Email Trigger extension.
    """
    mail_ref = db.collection("mail")
    await mail_ref.add(
        {
            "to": user_email,
            "message": {
                "subject": f'Your story "{story_title}" is ready!',
                "html": f"""
                <h1>Your story is complete!</h1>
                <p>Great news! Your story "{story_title}" has been generated and is ready for you to explore.</p>
                <p>You can view your story by clicking on the link below:</p>
                <a href="https://yourdomain.com/stories/{story_id}">View Your Story</a>
                <p>We hope you enjoy your newly created story!</p>
                <p>Best regards,<br>The Storytopia Team</p>
            """,
            },
        }
    )
