from .BaseController import BaseController
from ..models import Project, DataChunk
from ..stores import LLMEnums
from typing import List


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
    
    def insert_into_vectordb(self, project: Project, chunks: List[DataChunk], do_rest: bool= False):
        # Step1: get collection name of project
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # Step2: manage data of chunks
        texts = [
            chunk.chunk_text
            for chunk in chunks
        ]
        metadatas = [
            chunk.chunk_metadata
            for chunk in chunks
        ]
        
        vectors = [
            self.embedding_client.embed_text(text=chunk.chunk_text, document_type=LLMEnums.DocumentTypeEnums.DOCUMENT.value)
            for chunk in chunks
        ]
        # Step3: create collection in vectordb if not exist
        _ = self.vectordb_provider.create_collection(collection_name=collection_name, 
                                                 embedding_size=self.embedding_client.embedding_size, 
                                                 do_rest=do_rest
                                                 )
        # Step4: insert data into vectordb collection
        _ = self.vectordb_provider.insert_many(collection_name=collection_name, texts=texts, vectors=vectors, metadatas=metadatas)
        
        return True
    
    
        