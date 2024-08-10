from typing import List
import os
from google.cloud import storage
from openai import OpenAI
import requests
import asyncio
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()


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

    async def generate_images(self, scene_descriptions: List[str]) -> List[str]:
        image_urls = []
        for index, description in enumerate(scene_descriptions):
            try:
                # Generate image using DALL-E 3
                response = self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=description,
                    size="1792x1024",
                    quality="standard",
                    n=1,
                )

                # Get the generated image URL
                image_url = response.data[0].url

                # Download the image
                image_content = requests.get(image_url).content

                # Upload to Google Cloud Storage in the specified folder
                blob_name = f"{self.folder_name}/scene_{index + 1}.png"
                blob = self.bucket.blob(blob_name)
                blob.upload_from_string(image_content, content_type="image/png")

                # Make the blob publicly accessible
                blob.make_public()

                # Add the public URL to the list
                image_urls.append(blob.public_url)

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error generating image for scene {index + 1} with prompt '{description}': {str(e)}",
                )

        return image_urls

    def create_folder_if_not_exists(self):
        """Create the folder in the bucket if it doesn't exist."""
        blob = self.bucket.blob(f"{self.folder_name}/")
        if not blob.exists():
            blob.upload_from_string("")


# Factory function to create ImageGenerationService
# def create_image_generation_service(
#     openai_api_key: str,
#     gcs_bucket_name: str,
#     folder_name: str = "storytopia_dev",
# ) -> ImageGenerationService:
#     openai_client = OpenAI(api_key=openai_api_key)
#     storage_client = storage.Client()
#     return ImageGenerationService(
#         openai_client=openai_client,
#         storage_client=storage_client,
#         bucket_name=gcs_bucket_name,
#         folder_name=folder_name,
#     )


# # Test script
# async def test_image_generation_service():
#     # Load environment variables
#     openai_api_key = os.getenv("OPENAI_API_KEY")
#     gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")

#     if not openai_api_key or not gcs_bucket_name:
#         print(
#             "Error: Please set OPENAI_API_KEY and GCS_BUCKET_NAME environment variables."
#         )
#         return

#     # Create the service
#     service = create_image_generation_service(
#         openai_api_key=openai_api_key,
#         gcs_bucket_name=gcs_bucket_name,
#         folder_name="storytopia_test_images",
#     )

#     # Create the folder if it doesn't exist
#     service.create_folder_if_not_exists()

#     # Sample scene descriptions
#     scene_descriptions = [
#         "A vibrant Mexican marketplace with colorful piñatas hanging from the ceiling",
#         "A serene Mayan temple surrounded by lush jungle at sunset",
#         "A festive Day of the Dead celebration with decorated sugar skulls and marigolds",
#     ]

#     try:
#         # Generate images
#         image_urls = await service.generate_images(scene_descriptions)

#         # Print results
#         print("Generated image URLs:")
#         for i, url in enumerate(image_urls, 1):
#             print(f"Scene {i}: {url}")

#     except Exception as e:
#         print(f"An error occurred: {str(e)}")


# if __name__ == "__main__":
#     asyncio.run(test_image_generation_service())
