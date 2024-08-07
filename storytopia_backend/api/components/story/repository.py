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