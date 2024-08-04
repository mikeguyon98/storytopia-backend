"""
This module defines the API routes for user-related operations.

It sets up the FastAPI router and includes a route to retrieve the current user.

Modules:
    fastapi: FastAPI framework for building APIs.
    storytopia_backend.api.middleware.auth: Middleware for authentication.
    .model: User model definition.

Functions:
    read_user: Retrieve the current user.
"""
from fastapi import APIRouter, Depends
from storytopia_backend.api.middleware.auth import get_current_user
from .model import User

router = APIRouter()

@router.get("/", response_model=User)
async def read_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Retrieve the current user.
    
    Parameters:
        current_user (User): The current user object.
    
    Returns:
        User: The current user.
    """
    return current_user
