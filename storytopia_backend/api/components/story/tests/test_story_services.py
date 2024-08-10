import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from storytopia_backend.api.components.story.model import Story, StoryPost
from storytopia_backend.api.components.story.services import (
    create_user_story,
    get_story,
)
from storytopia_backend.api.components.user.model import User


@pytest.fixture
def mock_current_user():
    return User(
        id="user123",
        username="testuser",
        profile_picture="https://example.com/profile.jpg",
        bio="Test user bio",
        followers=[],
        following=[],
        liked_books=[],
        saved_books=[],
        public_books=[],
        private_books=[],
        createdAt=datetime.now(timezone.utc).isoformat(),
    )


@pytest.fixture
def mock_story_post():
    return StoryPost(
        title="Test Story", description="This is a test story", private=False
    )


@pytest.fixture
def mock_story():
    return Story(
        title="Test Story",
        description="This is a test story",
        author="testuser",
        author_id="user123",
        createdAt=datetime.now(timezone.utc).isoformat(),
        private=False,
        story_pages=[],
        story_images=[],
        likes=0,
        saves=0,
        id="story123",
    )


@pytest.mark.asyncio
@patch("storytopia_backend.api.components.story.services.create_story")
async def test_create_user_story(mock_create_story, mock_current_user, mock_story_post):
    mock_create_story.return_value = "story123"

    result = await create_user_story(mock_story_post, mock_current_user)

    assert isinstance(result, Story)
    assert result.title == mock_story_post.title
    assert result.description == mock_story_post.description
    assert result.author == mock_current_user.username
    assert result.author_id == mock_current_user.id
    assert result.private == mock_story_post.private
    assert result.id == "story123"


@pytest.mark.asyncio
@patch("storytopia_backend.api.components.story.services.get_story_by_id")
async def test_get_story_success(mock_get_story_by_id, mock_story):
    mock_get_story_by_id.return_value = mock_story

    result = await get_story("story123", "user123")

    assert result == mock_story


@pytest.mark.asyncio
@patch("storytopia_backend.api.components.story.services.get_story_by_id")
async def test_get_story_not_found(mock_get_story_by_id):
    mock_get_story_by_id.return_value = None

    result = await get_story("nonexistent_story", "user123")

    assert result == {"message": "Story not found"}


@pytest.mark.asyncio
@patch("storytopia_backend.api.components.story.services.get_story_by_id")
async def test_get_private_story_unauthorized(mock_get_story_by_id, mock_story):
    private_story = mock_story.model_copy(update={"private": True})
    mock_get_story_by_id.return_value = private_story

    result = await get_story("story123", "unauthorized_user")

    assert result == {"message": "Story is private"}


@pytest.mark.asyncio
@patch("storytopia_backend.api.components.story.services.get_story_by_id")
async def test_get_private_story_authorized(mock_get_story_by_id, mock_story):
    private_story = mock_story.model_copy(update={"private": True})
    mock_get_story_by_id.return_value = private_story

    result = await get_story("story123", "user123")

    assert result == private_story
