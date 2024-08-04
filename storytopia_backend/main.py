"""
This module contains the main FastAPI application.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from storytopia_backend.models import User
from storytopia_backend.auth_utils import get_current_user


app = FastAPI()

@app.get("/user", response_model=User)
async def read_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Retrieve the current user.
    
    Parameters:
        current_user (User): The current user object.
    
    Returns:
        User: The current user.
    """
    return current_user


origins = [
    "http://localhost:3000",  # Replace with your actual origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
