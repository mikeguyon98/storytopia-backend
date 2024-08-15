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
        Generate educational content based on the given prompt, considering any specified disability.

        Args:
        - prompt (str): The educational topic or concept to explore.
        - disability (str, optional): The specific disability to consider (e.g., "color blindness", "dyslexia").

        Returns:
        - str: A JSON string containing the prompt, title, detailed visual descriptions, and educational text for each concept.
        """
        disability_consideration = ""
        if disability:
            disability_consideration = f"""
            Consider the following disability when generating the content: {disability}
            - For visual descriptions, ensure they are accessible and meaningful for individuals with this disability.
            - For educational text, adapt the explanations and examples to be more inclusive and effective for learners with this disability.
            """

        full_prompt = f"""
        Generate educational content with a concise title and 10 concept descriptions based on the following prompt: {prompt}

        {disability_consideration}

        The output should be a JSON object with the following structure:
        {{
            "Prompt": "The original prompt",
            "Title": "The educational topic title",
            "Scenes": [
                "Scene 1 content",
                "Scene 2 content",
                ...
            ],
            "Summaries": [
                "Summary for Scene 1",
                "Summary for Scene 2",
                ...
            ]
        }}

        For each detailed visual description in "Scenes":
        - Focus on clear, visually descriptive elements that illustrate the educational concept.
        - Include relevant visual details about examples or scenarios that explain the concept.
        - Ensure the visual descriptions contribute to a cohesive and engaging educational narrative.
        - Keep the description suitable for a general audience, avoiding any sensitive or controversial content.
        - If a disability is specified, ensure the descriptions are accessible and meaningful for individuals with that disability.

        For each educational text in "Summaries":
        - Provide 3 to 4 sentences of engaging and informative text for each concept.
        - Explain the concept clearly and concisely, making it educational and enjoyable for readers.
        - Relate the text to the visual description to reinforce learning.
        - If a disability is specified, adapt the explanations and examples to be more inclusive and effective for learners with that disability.

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
                        "Scene 1 content",
                        "Scene 2 content",
                        ...
                    ],
                    "Summaries": [
                        "Summary for Scene 1",
                        "Summary for Scene 2",
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
