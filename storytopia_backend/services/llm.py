import json
from typing import List
import os
import asyncio
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()


class StoryGenerationService:
    def __init__(self, project_id: str, location: str, model_name: str):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)

    async def generate_story(self, prompt: str) -> List[str]:
        """
        Generate a multi-scene comic book story based on the given prompt.

        Args:
        - prompt (str): The prompt for the story.

        Returns:
        - str: A JSON string containing the prompt, title, detailed scenes, and brief scenes.
          The JSON structure is:
          {
              "Prompt": string,
              "Title": string,
              "Scenes": List[string],
              "Summaries": List[string]
          }
        """
        full_prompt = f"""
        Generate a comic book story title and 10 scene descriptions based on the following prompt: {prompt}

        The output should be a JSON object with the following structure:
        {{
            "Prompt": "The original prompt",
            "Title": "The story title",
            "Scenes": [
                "Detailed scene 1 description",
                "Detailed scene 2 description",
                ...
            ],
            "Summaries": [
                "Brief scene 1 summary",
                "Brief scene 2 summary",
                ...
            ]
        }}

        For each detailed scene description in "Scenes":
        - Be vivid and visual, focusing on what can be seen in a single image.
        - Include important visual details about characters, setting, and action.
        - Contribute to a coherent overall narrative arc.
        - Add conversation dialogue (subtitle) for the character if needed.
        - Length can vary as needed to fully describe the scene.

        For each brief scene summary in "Summaries":
        - Provide a concise summary of the scene, around 2-3 sentences.
        - Make it engaging and enjoyable for readers to read.

        Ensure the output is valid JSON format with matching numbers of detailed scenes and summaries.
        """
        response = self.model.generate_content(full_prompt)
        generated_text = response.text

        try:
            json.loads(generated_text)  # Just to validate JSON structure
            return generated_text  # Return the original JSON string if valid
        except json.JSONDecodeError:
            # If parsing fails, return a simple error JSON
            return json.dumps(
                {
                    "Prompt": prompt,
                    "Title": "Error: Invalid JSON generated",
                    "Scenes": ["Error: Unable to generate valid story data"],
                    "Summaries": ["Error: Unable to generate scene summaries"],
                }
            )


# # Sample test
# if __name__ == "__main__":
#     # Create StoryGenerationService instance
#     story_service = StoryGenerationService(
#         os.getenv("GOOGLE_CLOUD_PROJECT"),
#         os.getenv("GOOGLE_CLOUD_LOCATION"),
#         "gemini-1.5-pro",
#     )

#     # Test generate_story function
#     test_prompt = "Nobel Prize Winner in Chemistry wins UFC Welterweight Title"
#     testing_story_parts = asyncio.run(story_service.generate_story(test_prompt))
#     print(testing_story_parts)
