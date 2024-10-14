from ..LLMInterface import LLMInterface
from ..OpenAIEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    
    def __init__(
            self,
            api_key: str,
            api_url: str= None, # this url to can use any provider other openai but usin openai behavior
            defualt_input_max_characters: int= 1000,
            defualt_generation_max_output_tokens: int= 1000,
            defualt_generation_temperature: float= 0,
        ):
        
        self.api_key = api_key
        self.api_url = api_url

        self.defualt_input_max_characters = defualt_input_max_characters
        self.defualt_generation_max_output_tokens = defualt_generation_max_output_tokens
        self.defualt_generation_temperature = defualt_generation_temperature


        # Set general properties to can be used generally within instances
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        # Client to can access the llms provider
        self.client = OpenAI(
            api_key=self.api_key,
            api_url=self.api_url
        )

        # Create a logger to moniter connections and generations
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: int):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt, chat_history: list= [], max_output_tokens: int= None, temperature: float= None):
        # Check the client status
        if not self.client:
            self.logger.error("OpenAI client was not setted!")
            return None
        
        # Check the generation model status
        if not self.generation_model_id:
            self.logger.error("Generation model was not setted!")
            return None
        
        # Setting default parameters if use not set
        max_output_tokens = max_output_tokens if max_output_tokens else self.defualt_generation_max_output_tokens
        temperature = temperature if temperature else self.defualt_generation_temperature

        # Update chat history with user prompt
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value) # Set the prompt as required structure
        )

        # Generate respone
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature
        )

        # Check the status of response
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message or len(response.choices[0].message["content"]) == 0:
            self.logger.error("Error occured while generating text using OpenAI!")
            return None
        
        # Return generated response
        return response.choices[0].message["content"]

    def embed_text(self, text, document_type = None):
        
        # Check the client status
        if not self.client:
            self.logger.error("OpenAI client was not setted!")
            return None
        
        # Check the embedding model status
        if not self.embedding_model_id:
            self.logger.error("Embedding model was not setted!")
            return None
        
        # Generate the response
        response = self.client.embeddings.create(
            model= self.embedding_model_id,
            input= text
        )

        # Check the response status
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error occured while embedding the text using OpenAI!")
            return None

        # Return the embedding vector of text
        return response.data[0].embedding    
    

    
    def construct_prompt(self, prompt: str, role: str):
        # return the prompt details as a dictionary
        return {
            "role": role,
            "content": self.process_text(prompt) # clean the content before setting it
        }
    
    # This method used to set number of characters limitation for text (not abstracted)
    def process_text(self, text: str):
        return text[:self.defualt_input_max_characters].strip()

        