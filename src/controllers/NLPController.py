from .BaseController import BaseController
from models import Project, DataChunk
from stores import LLMEnums, DocumentTypeEnums
from typing import List
import json

class NLPController(BaseController):
    def __init__(self, vectordb_provider, embedding_client, generation_client, template_parser):
        super().__init__()
        self.vectordb_provider = vectordb_provider
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.template_parser = template_parser
        
        
    def create_collection_name(self, project_id: str):
        # create a collection name consists of project id
        return f"Collection_{project_id}".strip()
    
    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        return self.vectordb_provider.delete_collection(collection_name=collection_name)
    
    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        collection_info = self.vectordb_provider.get_collection_info(collection_name=collection_name)
        
        #Serialize the collection_info as a dictionary
        return json.loads(
            json.dumps(collection_info, default=lambda o: o.__dict__) # serialize the collection_info as a json string format
            )
    
    def insert_into_vectordb(self, project: Project, chunks: List[DataChunk], chunks_ids: List[int], do_rest: bool= False):
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
            self.embedding_client.embed_text(text=chunk.chunk_text, document_type=DocumentTypeEnums.DOCUMENT.value)
            for chunk in chunks
        ]
        # Step3: create collection in vectordb if not exist
        _ = self.vectordb_provider.create_collection(collection_name=collection_name, 
                                                 embedding_size=self.embedding_client.embedding_size, 
                                                 do_rest=do_rest
                                                 )
        # Step4: insert data into vectordb collection
        _ = self.vectordb_provider.insert_many(collection_name=collection_name, texts=texts, vectors=vectors, metadatas=metadatas, record_ids=chunks_ids)
        
        return True
    
    def search_vector_db_collection(self, project: Project, text: str, limit: int=6):
        
        # Step1: get collection name of project
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # Step2: embed the text
        embeded_text = self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnums.QUERY.value)
        
        # Step3: search the vectordb collection
        search_results = self.vectordb_provider.search_by_vector(collection_name=collection_name, vector=embeded_text, limit=limit)
        
        if not search_results or len(search_results) == 0:
            return False
        
        return search_results
    
    
    def answer_rag_question(self, project: Project, query: str, limit: int=16):
        
        answer, full_prompt, chat_history = None, None, None
        
        # step1: get related documents
        retrieved_documents = self.search_vector_db_collection(project=project, text=query, limit=limit)
        
        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # Step2: construct llm prompt
        system_message = self.template_parser.get("rag", "sysetm_prompt")
        
        documents_prompt = "\n".join(
            [
                self.template_parser.get(
                    "rag", 
                    "Document_format", 
                    {
                        "doc_no": idx + 1,
                        "content": doc.text
                    }
                )
                for idx, doc in enumerate(retrieved_documents)
            ]
        )
        
        footer_prompt = self.template_parser.get("rag", "footer", {"query": query})
        
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_message,
                role=self.generation_client.enums.SYSTEM.value
            )
        ]
        
        full_prompt = "\n\n".join(
            [
                documents_prompt,
                footer_prompt
            ]
        )
        
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )
        
        return answer, full_prompt, chat_history
        
        