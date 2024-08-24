import json
import vertexai
import os
from sqlalchemy import create_engine, text
from sqlalchemy import URL
from vertexai.generative_models import GenerativeModel, GenerationConfig
from llama_index.readers.web import SimpleWebPageReader
from storytopia_backend.services.vector_db import TiDBVectorService
from dotenv import load_dotenv
import jsonschema
from storytopia_backend.services.wikipedia_service import wikipedia_search


load_dotenv()


class StoryGenerationService:
    def __init__(self, project_id: str, location: str, model_name: str):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        self.response_schema = {
            "type": "object",
            "properties": {
                "Prompt": {"type": "string"},
                "Title": {"type": "string"},
                "Scenes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "Summaries": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["Prompt", "Title", "Scenes", "Summaries"],
        }

    async def generate_story(self, prompt: str, disability: str = None) -> str:
        """
        Generate an educational story based on the given prompt, considering any specified disability.
        Args:
        - prompt (str): The educational topic or concept to explore.
        - disability (str, optional): The specific disability to consider (e.g., "color blindness", "dyslexia").
        Returns:
        - str: A JSON string containing the story elements.
        """
        TIDB_USERNAME = os.getenv("TIDB_USERNAME")
        TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
        TIDB_HOST = os.getenv("TIDB_HOST")
        wiki_vector_service = TiDBVectorService(TIDB_USERNAME, TIDB_PASSWORD, TIDB_HOST, database="wiki")

        wiki_vector_service.setup_index(user_id="temp_wiki")


        def do_prepare_data(url):
            documents = SimpleWebPageReader(html_to_text=True).load_data([url,])
            print(documents)
            wiki_vector_service.add_documents(documents)
        
        def delete_all_data(table_name, database_name):
            # Create the database URL
            tidb_connection_url = URL(
                "mysql+pymysql",
                username=os.environ['TIDB_USERNAME'],
                password=os.environ['TIDB_PASSWORD'],
                host=os.environ['TIDB_HOST'],
                port=4000,
                database=database_name,
                query={"ssl_verify_cert": True, "ssl_verify_identity": True},
            )
    
            # Create the SQLAlchemy engine
            engine = create_engine(tidb_connection_url)
            
            # SQL command to delete all data
            delete_command = text(f"DELETE FROM {table_name}")
            
            # Execute the command
            with engine.connect() as connection:
                connection.execute(delete_command)
                connection.commit()
            
            print(f"All data deleted from table '{table_name}'")

        disability_consideration = ""
        if disability:
            disability_consideration = f"""
            Consider the following disability when crafting the story: {disability}
            - Ensure all descriptions and explanations are accessible and meaningful for individuals with this disability.
            - Adapt the narrative, examples, and learning elements to be inclusive and effective for learners with this disability.
            """
        wiki_articles = None
        result = None
        try:
            wiki_articles = wikipedia_search(prompt)
        except Exception as e:
            print(f"Error searching Wikipedia: {str(e)}")
        wiki_urls = []
        try:
            if wiki_articles:
                wiki_urls = [article["url"] for article in wiki_articles]
            wiki_vector_service.setup_index(user_id="temp_wiki")
            print(wiki_urls)
            for url in wiki_urls:
                do_prepare_data(url)
            result = wiki_vector_service.query(prompt)
            print(result)
            # Delete all data from the table
            delete_all_data("temp_wiki", "wiki")
        except Exception as e:
            print(f"Error processing Wikipedia articles: {str(e)}")


        full_prompt = f"""
        CONTEXT:
        {result}

        PROMPT:
        Generate a comic book story title and 10 scene descriptions based on the following prompt: {prompt}

        Ensure the output is in valid JSON format with the following structure:
        
        "Prompt": "The original user prompt (exactly as provided)",
        "Title": "The generated story title",
        "Scenes": ["Scene 1 description", "Scene 2 description", ..., "Scene 10 description"],
        "Summaries": ["Summary 1", "Summary 2", ..., "Summary 10"]

        For each scene in "Scenes" (create exactly 10 scenes):
        - Focus on clear, visually descriptive elements that can be depicted in a single image.
        - Include relevant visual details about characters, setting, and action.
        - Ensure the scenes contribute to a cohesive and engaging narrative arc.
        - Dialogue (subtitle) should be brief and contribute positively to the story.
        - Keep the description suitable for a general audience, avoiding any sensitive or controversial content.
        - Ensure there are no copyright issues by not requesting specific copyrighted characters, logos, or branded content.
        - Avoid requesting images of real people, especially public figures or celebrities.
        - Don't include explicit violence, gore, or disturbing imagery in your prompts.
        - Avoid prompts that could generate hate speech, discriminatory content, or extreme political imagery.

        For each summary in "Summaries" (create exactly 10 summaries, one for each scene):
        - Provide story text for each scene, each around 3 to 4 sentences
        - Make it engaging, enjoyable and educational for readers to read.

        {disability_consideration}
        """

        response = self.model.generate_content(
            full_prompt,
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.response_schema,
            ),
        )

        return await self._self_heal_response(response.text, prompt, full_prompt)

    async def _self_heal_response(
        self,
        response_text: str,
        original_prompt: str,
        full_prompt: str,
        attempts: int = 3,
    ) -> str:
        """
        Attempt to self-heal the response if it's not valid JSON or doesn't follow the schema.
        Args:
        - response_text (str): The original response text from the model.
        - original_prompt (str): The original prompt entered by the user.
        - full_prompt (str): The full prompt used to generate the story.
        - attempts (int): The number of attempts to self-heal (default: 3).
        Returns:
        - str: A valid JSON string containing the story elements.
        Raises:
        - ValueError: If unable to generate a valid response after the specified number of attempts.
        """
        for i in range(attempts):
            try:
                response_json = json.loads(response_text)
                jsonschema.validate(instance=response_json, schema=self.response_schema)

                # Ensure the Prompt field matches the original user prompt
                if response_json["Prompt"] != original_prompt:
                    response_json["Prompt"] = original_prompt
                    response_text = json.dumps(response_json)

                return response_text
            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                if i == attempts - 1:
                    raise ValueError(
                        f"Unable to generate a valid response after {attempts} attempts: {str(e)}"
                    )

                heal_prompt = f"""
                The previous response was invalid or incomplete. Please fix the following issues and regenerate the story:
                Error: {str(e)}
                Original user prompt: {original_prompt}
                Full prompt used: {full_prompt}
                Previous response: {response_text}
                Please ensure the output is in valid JSON format and follows this schema:
                {json.dumps(self.response_schema, indent=2)}
                Make sure the "Prompt" field contains the exact original user prompt: "{original_prompt}"
                Ensure there are exactly 10 Scenes and 10 Summaries.
                """

                response = self.model.generate_content(
                    heal_prompt,
                    generation_config=GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=self.response_schema,
                    ),
                )
                response_text = response.text

        raise ValueError(
            f"Unable to generate a valid response after {attempts} attempts"
        )
