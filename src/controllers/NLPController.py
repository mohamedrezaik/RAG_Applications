from .BaseController import BaseController
from ..models import Project


class NLPController(BaseController):
    def __init__(self, vectordb_provider, embedding_client, generation_client):
        super().__init__()
        self.vectordb_provider = vectordb_provider
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        
        
    def create_collection_name(self, project_id: str):
        # create a collection name consists of project id
        return f"Collection_{project_id}".strip()
    
    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project=project.project_id)
        
        return self.vectordb_provider.delete_collection(collection_name=collection_name)
    
    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project=project.project_id)
        
        collection_info = self.vectordb_provider.get_collection_info(collection_name=collection_name)
        
        return collection_info
    
    
        