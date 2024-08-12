from typing import List
import os
from google.cloud import storage
from openai import OpenAI
import requests
import uuid
from datetime import datetime
import asyncio
from fastapi import HTTPException
from dotenv import load_dotenv
import time
import random

load_dotenv()


class ImageGenerationError(Exception):
    """Base class for image generation errors."""

    pass


class ImageUploadError(ImageGenerationError):
    """Raised when there's an error uploading the image to storage."""

    pass


class MaxRetriesExceededError(ImageGenerationError):
    """Raised when the maximum number of retries is exceeded."""

    pass


class ImageGenerationService:
    def __init__(
        self,
        openai_client: OpenAI,
        storage_client: storage.Client,
        bucket_name: str,
        folder_name: str,
    ):
        self.openai_client = openai_client
        self.storage_client = storage_client
        self.bucket_name = bucket_name
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.folder_name = folder_name

    async def generate_images(
        self, scene_descriptions: List[str], style: str
    ) -> List[str]:
        image_urls = []
        for index, description in enumerate(scene_descriptions):
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    # Generate image using DALL-E 3
                    response = self.openai_client.images.generate(
                        model="dall-e-3",
                        prompt=f"{description} | Remove all dialogue/text in image. Use this artistic style for the image: {style}",
                        size="1792x1024",
                        quality="standard",
                        n=1,
                    )
                    # Get the generated image URL
                    image_url = response.data[0].url
                    # Download the image
                    image_content = requests.get(image_url).content

                    # Generate a timestamp
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                    # Create a unique blob name using the timestamp
                    blob_name = f"{self.folder_name}/scene_{index + 1}_{timestamp}.png"

                    blob = self.bucket.blob(blob_name)
                    blob.upload_from_string(image_content, content_type="image/png")
                    # Make the blob publicly accessible
                    blob.make_public()
                    # Add the public URL to the list
                    image_urls.append(blob.public_url)
                    break  # Successfully generated and uploaded the image, exit the retry loop
                except Exception as e:
                    print(f"Error generating image for scene {index + 1}: {str(e)}")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        print(f"Retrying... Attempt {retry_count + 1} of {max_retries}")
                        # Regenerate the description
                        new_description = await self.regenerate_description(description)
                        description = new_description
                        # Add a small delay before retrying
                        await asyncio.sleep(random.uniform(1, 3))
                    else:
                        error_msg = f"Failed to generate image after {max_retries} attempts for scene {index + 1}."
                        print(error_msg)
                        raise MaxRetriesExceededError(error_msg)

        if len(image_urls) != len(scene_descriptions):
            raise ImageGenerationError(
                f"Generated {len(image_urls)} images, but expected {len(scene_descriptions)}."
            )

        return image_urls

    async def regenerate_description(self, original_description: str) -> str:
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that rewrites image descriptions to avoid policy violations while maintaining the essence of the original description.",
                    },
                    {
                        "role": "user",
                        "content": f"Please rewrite the following image description to avoid potential policy violations, while keeping the main idea intact: '{original_description}'",
                    },
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error regenerating description: {str(e)}")
            return original_description  # Return the original description if regeneration fails

    def create_folder_if_not_exists(self):
        """Create the folder in the bucket if it doesn't exist."""
        blob = self.bucket.blob(f"{self.folder_name}/")
        if not blob.exists():
            blob.upload_from_string("")
