from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnums
from .mongodb_schemas import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne # Operation type(insert on record)


class ChunkDataModel(BaseDataModel):

    def __init__(self, db_client):
        # Make the parent (BaseDataModel) see the db_client
        super().__init__(db_client)

        # Get the data chunk collection
        self.collection = self.db_client[DataBaseEnums.COLLECTION_DATA_CHUNK.value]

    # A method to insert on chunk into database
    async def insert_chunk(self, chunk: DataChunk):
        
        # Insert the "chunk" into mongodb collection
        result = self.collection.insert_one(chunk.model_dump())

        # Store the mongodb "_id" into our chunk
        chunk._id = result.inserted_id

        return chunk
    

    # A method to get a specific chunk from mongodb collection
    async def get_chunk(self, chunk_id: str):

        # Query to get the specific data of "_id"
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)}) # we convert the "chunk_id" into "ObjectId" type because it's stored in this type in mongodb collection

        if result is None:
            # If there is no data for this chunk
            return None
    
        data_chunk = DataChunk(**result)
        data_chunk._id = result["_id"] # We have to set it manually(exiplicitly) because it's dealed as a protected property
        return data_chunk
    

    # A method to insert chunks as batchs(it's more efficient to insert large number of chunks(instead of one by one) for our database)
    async def insert_batch_chunks(self, chunks: list, batch_size: int=100):
        capacity = len(chunks)

        for i in range(0, capacity, batch_size):

            # Get the batch of chunks equal "chunk_size"
            batch = chunks[i: (i + batch_size)]

            # Store our chunks and thier operation type as a list
            operations = [
                # This type used to create a bulk of documents list of chunks to be writted into mongodb collection as a batch
                InsertOne(chunk.model_dump())    
                for chunk in batch
            ]

            # Insert a bulk batch into mongodb collection
            await self.collection.bulk_write(operations)


        # Return number of chunks inserted
        return capacity
    
    # A method to delete the chunks of a specific project with "project_id" from mognodb data collection
    async def delete_chunks_by_project_id(self, project_id: ObjectId):

        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        # Return number of deleted chunks
        return result.deleted_count


