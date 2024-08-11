from typing import List
from storytopia_backend.firebase_config import db
from .model import Story

def get_all_stories():
    """
    Get all stories.
    """
    stories = db.collection('stories').stream()
    return [Story(**story.to_dict()) for story in stories]

async def create_story(story_data: dict) -> str:
    story_ref = db.collection('stories').document()  # Create a new document reference with a unique ID
    story_id = story_ref.id
    print("story_id", story_id)
    story_data['id'] = story_id  # Add the ID to the document data
    story_ref.set(story_data)
    return story_id

async def get_story_by_id(story_id: str) -> Story:
    print("+++++++++++++++++++++++++++++++++++++++")
    story_ref = db.collection('stories').document(story_id)
    print("story_ref", story_ref)
    story_doc = story_ref.get()
    print("story_doc", story_doc)
    return Story(**story_doc.to_dict()) if story_doc.exists else None

async def get_recent_public_stories_from_db(skip: int, limit: int) -> List[Story]:
    """
    Retrieve the most recently created public stories from the database.

    Parameters:
        skip (int): The number of records to skip for pagination.
        limit (int): The number of records to return.

    Returns:
        List[Story]: A list of the most recent public stories.
    """
    stories_ref = db.collection('stories')
    query = (
        stories_ref
        .where("private", "==", False)
        .order_by("createdAt", direction="DESCENDING")
        .offset(skip)
        .limit(limit)
    )
    story_docs = query.stream()
    stories = [Story(**doc.to_dict()) for doc in story_docs]
    return stories

async def update_story(story: Story) -> None:
    """
    Update a story's information in the database.

    Parameters:
        story (Story): The story object containing updated information.

    Returns:
        None
    """
    story_ref = db.collection('stories').document(story.id)
    story_ref.set(story.dict())
