"""
This module defines the data models used in the application.

It includes the Story model which represents a story with its metadata and content.
Classes:
    Story: Represents a story with its metadata and content.
"""
from typing import List

from pydantic import BaseModel

class Story(BaseModel):
    """
    Represents a story with its metadata and content.

    Attributes:
        title (str): The title of the story.
        author (str): The author of the story.
        author_id (str): The unique identifier of the author.
        description (str): The description of the story.
        story_pages (List[str]): A list of pages in the story.
        story_images (List[str]): A list of images in the story.
        private (bool): Indicates if the story is private.
        createdAt (str): The creation date of the story.
        id (str): The unique identifier of the story.
        likes (int): The number of likes the story has received.
        saves (int): The number of times the story has been saved.
    """
    title: str
    author: str
    author_id: str
    description: str
    story_pages: List[str]
    story_images: List[str]
    private: bool
    createdAt: str
    id: str
    likes: int
    saves: int

class StoryPost(BaseModel):
    """
    Represents a story post with its metadata and content.

    Attributes:
        title (str): The title of the story.
        description (str): The description of the story.
        private (bool): Indicates if the story is private.
    """
    title: str
    description: str
    private: bool