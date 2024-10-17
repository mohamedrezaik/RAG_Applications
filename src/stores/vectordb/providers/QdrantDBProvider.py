from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List


class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, distance_method: str= DistanceMethodEnums.DOT.value): # Distance method represents the similarty measurements to query by
        
        self.client = None
        self.db_path = db_path

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE

        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        # Initializing the logger to log the errors
        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None # As there is no specific way to disconnect we just set the client to None

    def is_collection_existed(self, collection_name: str) -> bool:

        return self.client.collection_exists(collection_name=collection_name)
        
    def list_all_collections(self) -> List:
        
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        # Return all details about the required collection
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str) -> bool:

        if not self.is_collection_existed(collection_name=collection_name):
            return False
        
        _ = self.client.delete_collection(collection_name=collection_name)
        
        return True
        
    def create_collection(self, collection_name: str, embedding_size: int, do_rest: bool= False):
        if do_rest:
            self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method),
            )

            return True
        
        return False
    

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict= None, record_id: str= None):

        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={
                            "metadata": metadata,
                            "text": text
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False
        
        return True
    
    def insert_many(self, collection_name: str, texts: list[str], vectors: list[list], metadatas: list[dict]= None, record_ids: list[str]= None, batch_size: int= 50):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can not insert new records to non-existed collection: {collection_name}")
            return False
        
        if metadatas is None:
            metadatas = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)
        
        # Split the whole batch into smaller batches with max size "batch_size"
        for i in range(0, len(texts), batch_size):
            texts_batch = texts[i: i + batch_size] 
            vectors_batch = vectors[i: i + batch_size]
            metadatas_batch = metadatas[i : i + batch_size]
            record_ids_batch = record_ids[i : i + batch_size]

            # Set records as one batch to be inserted to vector db
            batch_records = [
                models.Record(
                    vector=vectors_batch[x],
                    payload={
                        "text": texts_batch[x],
                        "metadata": metadatas_batch[x]
                    }
                )
                for x in range(0, len(texts_batch))
            ]

            try:
                # Insert into vector db
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                    )
            except Exception as e:
                self.logger.error(f"Error while inserting new records: {e}")
                return False

        return True
    
    def search_by_vector(self, collection_name: str, vector: list, limit: int= 5): # "vector" referes to the vector to search by in collection and "limit" referes to the number of returned similar vector to "vector"
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Can not search in non-existed collection: {collection_name}")
            return False
        
        return self.client.search(collection_name=collection_name, query_vector=vector, limit=limit)