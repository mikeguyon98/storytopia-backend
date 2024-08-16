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

    async def generate_story(self, prompt: str, disability: str = None) -> str:
        """
        Generate an educational story based on the given prompt, considering any specified disability.

        Args:
        - prompt (str): The educational topic or concept to explore.
        - disability (str, optional): The specific disability to consider (e.g., "color blindness", "dyslexia").

        Returns:
        - str: A JSON string containing the story elements.
        """
        disability_consideration = ""
        if disability:
            disability_consideration = f"""
            Consider the following disability when crafting the story: {disability}
            - Ensure all descriptions and explanations are accessible and meaningful for individuals with this disability.
            - Adapt the narrative, examples, and learning elements to be inclusive and effective for learners with this disability.
            """

        full_prompt = f"""
        Generate a comic book story title and 10 scene descriptions based on the following prompt: {prompt}

        The narrative should be educational, fun, and immersive, incorporating historical examples and interesting backgrounds.

        {disability_consideration}

        The output should be a JSON object with the following structure:
        {{
            "Prompt": "The original prompt",
            "Title": "A concise title",
            "Scenes": [
                "Scene 1: Vivid description of the story setting and action",
                "Scene 2: Continuation of the narrative with educational elements woven in",
                ...
            ],
            "Summaries": [
                ...
            ]
        }}

        For each scene in "Scenes" (create 10 scenes):
        - Describe an engaging part of the story that relates to the prompt.
        - Include vivid details about the characters, setting, or action that make the learning experience come alive.
        - Weave in educational content naturally, using the story elements to illustrate concepts.
        - Ensure each scene builds on the previous one to create a cohesive narrative arc.
        - If a disability is specified, make sure the descriptions are inclusive and meaningful for individuals with that disability.

        For each summary in "Summaries" (create 10 summaries, one for each scene):
        - Provide story text for each scene, each around 3 to 4 sentences
        - Make it engaging, enjoyable and educational for readers to read.
        - If a disability is specified, adapt the explanations to be more accessible and effective for learners with that disability.

        Ensure the output is in valid JSON format with 10 matching scenes and summaries.
        """

        response = self.model.generate_content(full_prompt)
        generated_text = response.text

        try:
            json.loads(generated_text)  # Validate JSON structure
            return generated_text  # Return the original JSON string if valid
        except json.JSONDecodeError:
            # If parsing fails, use GPT-4 to fix the JSON
            return await self._fix_json_with_gpt4(generated_text)

    async def _fix_json_with_gpt4(
        self, invalid_json: str, max_attempts: int = 3
    ) -> str:
        """
        Use GPT-4 to fix invalid JSON with multiple attempts.

        Args:
        - invalid_json (str): The invalid JSON string.
        - max_attempts (int): Maximum number of attempts to fix the JSON.

        Returns:
        - str: A valid JSON string.

        Raises:
        - ValueError: If unable to fix the JSON after max_attempts.
        """
        for attempt in range(max_attempts):
            try:
                prompt = f"""
                The following text was supposed to be a valid JSON object, but it contains errors. 
                Please fix the JSON and ensure it follows this structure:

                {{
                    "Prompt": "The original prompt",
                    "Title": "The educational topic title",
                    "Scenes": [
                        ...
                    ],
                    "Summaries": [
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

                # Validate the fixed JSON
                json.loads(fixed_json)
                return fixed_json

            except json.JSONDecodeError as e:
                if attempt == max_attempts - 1:
                    raise ValueError(
                        f"Failed to fix JSON after {max_attempts} attempts. Last error: {str(e)}"
                    )
                else:
                    print(f"Attempt {attempt + 1} failed. Retrying...")
                    # Use the output from the previous attempt as input for the next attempt
                    invalid_json = fixed_json

        # This line should never be reached due to the raise in the loop, but it's here for completeness
        raise ValueError(f"Failed to fix JSON after {max_attempts} attempts.")
