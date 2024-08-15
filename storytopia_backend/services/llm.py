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
        Generate educational content based on the given prompt.

        Args:
        - prompt (str): The educational topic or concept to explore.

        Returns:
        - str: A JSON string containing the prompt, title, detailed visual descriptions, and educational text for each concept.
        The JSON structure is:
        {
            "Prompt": string,
            "Title": string,
            "Scenes": List[string],
            "Summaries": List[string]
        }
        """
        full_prompt = f"""
        Generate educational content with a title and 10 concept descriptions based on the following prompt: {prompt}

        The output should be a JSON object with the following structure:
        {{
            "Prompt": "The original prompt",
            "Title": "The educational topic title",
            "Scenes": [
                "Detailed visual description 1",
                "Detailed visual description 2",
                ...
            ],
            "Summaries": [
                "Concept 1 educational text",
                "Concept 2 educational text",
                ...
            ]
        }}

        For each detailed visual description in "Scenes":
        - Focus on clear, visually descriptive elements that illustrate the educational concept.
        - Include relevant visual details about examples or scenarios that explain the concept.
        - Ensure the visual descriptions contribute to a cohesive and engaging educational narrative.
        - Keep the description suitable for a general audience, avoiding any sensitive or controversial content.
        - Ensure there are no copyright issues by not requesting specific copyrighted images, logos, or branded content.
        - Avoid requesting images of real people, especially public figures or celebrities.
        - Don't include explicit or disturbing imagery in your descriptions.
        - Avoid descriptions that could generate hate speech, discriminatory content, or extreme political imagery.

        For each educational text in "Summaries":
        - Provide 3 to 4 sentences of engaging and informative text for each concept.
        - Explain the concept clearly and concisely, making it educational and enjoyable for readers.
        - Relate the text to the visual description to reinforce learning.

        Ensure the output is valid JSON format with matching numbers of detailed visual descriptions and educational texts.
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
            "Title": "The educational topic title",
            "Scenes": [
                "Detailed visual description 1",
                "Detailed visual description 2",
                ...
            ],
            "Summaries": [
                "Concept 1 educational text",
                "Concept 2 educational text",
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
