"""
This module sets up the main API router for the application.

It imports the necessary components from FastAPI and the user controller,
initializes the main APIRouter instance, and includes the user router with
a specified prefix and tags.

Modules:
    fastapi: FastAPI framework for building APIs.
    .components.user.controller: User controller module containing user-related routes.
"""
from fastapi import APIRouter
from .components.user.controller import router as user_router
from .components.story.controller import router as story_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(story_router, prefix="/stories", tags=["stories"])
