from .LLMEnums import LLMEnums
from .providers import CoHereProvider, OpenAIProvider

class LLMProvidersFactory:
    
    def __init__(self, config: dict):
        self.config = config
    
    # A method to return the requested provider
    def ge_provider(self, provider):
        
        # Check if the requested provider is OpenAPI
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAPI_API_KEY,
                api_url=self.config.OPENAPI_URL_KEY,
                defualt_input_max_characters=self.config.DEFUALT_INPUT_MAX_CHARACTERS,
                defualt_generation_max_output_tokens=self.config.DEFUALT_GENERATION_MAX_OUTPUT_TOKENS,
                defualt_generation_temperature=self.config.DEFUALT_GENERATION_TEMPERATURE,
            )
        
        # Check if the requested provider is CoHere
        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                defualt_input_max_characters=self.config.DEFUALT_INPUT_MAX_CHARACTERS,
                defualt_generation_max_output_tokens=self.config.DEFUALT_GENERATION_MAX_OUTPUT_TOKENS,
                defualt_generation_temperature=self.config.DEFUALT_GENERATION_TEMPERATURE,
            ) 

        # Return None (no provider specified)
        return None