import os
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import storage
from storytopia_backend.services.stable_diffusion import ImageGenerationService
from storytopia_backend.services.llm import StoryGenerationService
from storytopia_backend.services.vector_db import TiDBVectorService

load_dotenv()

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
TIDB_USERNAME = os.getenv("TIDB_USERNAME")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_HOST = os.getenv("TIDB_HOST")

# Client initialization
openai_client = OpenAI(api_key=OPENAI_API_KEY)
storage_client = storage.Client()

# TiDB Vector Store setup
tidb_vector_service = TiDBVectorService(TIDB_USERNAME, TIDB_PASSWORD, TIDB_HOST)

# Service configurations
image_service_config = {
    "openai_client": openai_client,
    "storage_client": storage_client,
    "bucket_name": GCS_BUCKET_NAME,
    "folder_name": "storytopia_images_dev",
}

story_service_config = {
    "project_id": GOOGLE_CLOUD_PROJECT,
    "location": GOOGLE_CLOUD_LOCATION,
    "model_name": "gemini-1.5-pro",
}

# Service initialization
image_service = ImageGenerationService(**image_service_config)
story_service = StoryGenerationService(**story_service_config)

# Exports
__all__ = ["image_service", "story_service", "tidb_vector_service"]
