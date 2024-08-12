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

    async def generate_story(self, prompt: str, disabilities: str) -> List[str]:
        """
        Generate a multi-scene book story based on the given prompt.

        Args:
        - prompt (str): The prompt for the story.

        Returns:
        - str: A JSON string containing the prompt, title, detailed scenes, and story text to accompany each image.
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
        If there are disabilities listed here: {disabilities} then when you are generating the prompt keep in mind these disabilities, and make it so that a read
        with these disabilities could easily read the story. Only take into consideration disabilities that would effect the readers
        ability to read the story and do not make it obvious you know the disability, just write the story they would enjoy.
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
                "scene 1 story text",
                "scene 2 story text",
                ...
            ]
        }}

        For each detailed scene description in "Scenes":
        - Focus on clear, visually descriptive elements that can be depicted in a single image.
        - Include relevant visual details about characters, setting, and action.
        - Ensure the scenes contribute to a cohesive and engaging narrative arc.
        - Dialogue (subtitle) should be brief and contribute positively to the story.
        - Keep the description suitable for a general audience, avoiding any sensitive or controversial content.
        - Ensure there are no copyright issues by not requesting specific copyrighted characters, logos, or branded content.
        - Avoid requesting images of real people, especially public figures or celebrities.
        - Don't include explicit violence, gore, or disturbing imagery in your prompts.
        - Avoid prompts that could generate hate speech, discriminatory content, or extreme political imagery.

        For each story text in "Summaries":
        - Provide story text for each scenece, each around 3 to 4 sentences
        - Make it engaging, enjoyable and educational for readers to read.

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
