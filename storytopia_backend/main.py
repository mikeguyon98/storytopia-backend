"""
This module contains the main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from storytopia_backend.api.routes import router as api_router

load_dotenv()

app = FastAPI()

# Can add prefix as , prefix = "/api/v1/"
app.include_router(api_router)


@app.get("/")
async def root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the API"}

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)