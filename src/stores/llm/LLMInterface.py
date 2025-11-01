from abc import ABC, abstractmethod

# We will create the LLMInterface to be used with any provider class and with base abstracted methods(must be implemented in Providers classes)

class LLMInterface(ABC):

    # Building mandatory and common methods in all providers behaviors 

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int): # Note: embedding size is very important to can create a vector db with this embedding size
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int= None, temperature: float= None):
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str= None):
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass