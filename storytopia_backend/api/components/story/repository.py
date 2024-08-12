from typing import List
from storytopia_backend.firebase_config import db
from firebase_admin import auth
from .model import Story


def get_all_stories():
    """
    Get all stories.
    """
    stories = db.collection("stories").stream()
    return [Story(**story.to_dict()) for story in stories]


async def create_story(story_data: dict) -> str:
    story_ref = db.collection(
        "stories"
    ).document()  # Create a new document reference with a unique ID
    story_id = story_ref.id
    print("story_id", story_id)
    story_data["id"] = story_id  # Add the ID to the document data
    story_ref.set(story_data)
    return story_id


async def get_story_by_id(story_id: str) -> Story:
    print("+++++++++++++++++++++++++++++++++++++++")
    story_ref = db.collection("stories").document(story_id)
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
    stories_ref = db.collection("stories")
    query = (
        stories_ref.where("private", "==", False)
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
    story_ref = db.collection("stories").document(story.id)
    story_ref.set(story.model_dump())


async def get_user_email_by_uid(uid: str) -> str:
    """
    Retrieve the user's email address using their UID from Firebase Auth.

    Parameters:
        uid (str): The unique identifier of the user.

    Returns:
        str: The email address of the user, or None if not found.
    """
    try:
        user = auth.get_user(uid)
        return user.email
    except auth.AuthError:
        print(f"Error: Unable to find user with UID {uid}")
        return None


async def send_story_generation_email(user_id: str, story_description: str):
    """
    Send an email notification to the user about their generated story.

    Parameters:
        user_id (str): The ID of the user who generated the story.
        story_description (str): The description of the generated story.
    """
    user_email = await get_user_email_by_uid(user_id)
    if user_email:
        mail_ref = db.collection("mail").document()
        mail_ref.set(
            {
                "to": user_email,
                "message": {
                    "subject": "Your Story has been Generated!",
                    "html": f"""
                    <h1>Your Story is Ready!</h1>
                    <p>Hello,</p>
                    <p>We're excited to inform you that your story based on the prompt:</p>
                    <p><em>"{story_description}"</em></p>
                    <p>has been successfully generated.</p>
                    <p>Log in to your account to view and share your new creation!</p>
                    <p>Happy storytelling!</p>
                    <p>Best regards,<br>The Storytopia Team</p>
                """,
                },
            }
        )
    else:
        print(f"Error: Unable to find email for user {user_id}")


async def send_story_generation_failure_email(
    user_id: str, prompt: str, error_message: str
):
    """
    Send an email notification to the user about the failure in story generation.

    Parameters:
        user_id (str): The ID of the user who attempted to generate the story.
        prompt (str): The prompt used for story generation.
        error_message (str): The error message describing the failure.
    """
    user_email = await get_user_email_by_uid(user_id)
    if user_email:
        mail_ref = db.collection("mail").document()
        mail_ref.set(
            {
                "to": user_email,
                "message": {
                    "subject": "Story Generation Failed",
                    "html": f"""
                    <h1>We Encountered an Issue</h1>
                    <p>Hello,</p>
                    <p>We're sorry to inform you that we encountered an error while generating your story based on the prompt:</p>
                    <p><em>"{prompt}"</em></p>
                    <p>Error details: {error_message}</p>
                    <p>Please try again later or contact our support team if the issue persists.</p>
                    <p>We apologize for any inconvenience.</p>
                    <p>Best regards,<br>The Storytopia Team</p>
                """,
                },
            }
        )
    else:
        print(f"Error: Unable to find email for user {user_id}")
