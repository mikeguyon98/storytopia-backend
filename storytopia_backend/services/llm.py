import json
from typing import List
import os
import asyncio
import vertexai
from openai import OpenAI
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()


class StoryGenerationService:
    def __init__(
        self, project_id: str, location: str, model_name: str, openai_client: OpenAI
    ):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        self.openai_client = openai_client

    async def generate_story(self, prompt: str) -> str:
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
        - Provide story text for each scene, each around 3 to 4 sentences
        - Make it engaging, enjoyable and educational for readers to read.

        Ensure the output is valid JSON format with matching numbers of detailed scenes and summaries.
        """

        response = self.model.generate_content(full_prompt)
        generated_text = response.text

        try:
            json.loads(generated_text)  # Validate JSON structure
            return generated_text  # Return the original JSON string if valid
        except json.JSONDecodeError:
            # If parsing fails, use GPT-4 to fix the JSON
            return await self._fix_json_with_gpt4(generated_text)

    async def _fix_json_with_gpt4(self, invalid_json: str) -> str:
        """
        Use GPT-4 to fix invalid JSON.

        Args:
        - invalid_json (str): The invalid JSON string.

        Returns:
        - str: A valid JSON string.
        """
        prompt = f"""
        The following text was supposed to be a valid JSON object, but it contains errors. 
        Please fix the JSON and ensure it follows this structure:

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

        Make sure there are 10 scenes and 10 summaries.
        Here's the invalid JSON:

        {invalid_json}

        Please provide only the corrected JSON as your response, with no additional explanation.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that fixes JSON formatting issues.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        fixed_json = response.choices[0].message.content.strip()

        try:
            json.loads(fixed_json)  # Validate the fixed JSON
            return fixed_json
        except json.JSONDecodeError as e:
            raise ValueError(f"GPT-4 was unable to fix the JSON. Error: {str(e)}")
