from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnums
from .mongodb_schemas import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne # Operation type(insert on record)


class ChunkDataModel(BaseDataModel):

    def __init__(self, db_client: object):
        # Make the parent (BaseDataModel) see the db_client
        super().__init__(db_client)

        # Get the data chunk collection
        self.collection = self.db_client[DataBaseEnums.COLLECTION_DATA_CHUNK.value]

    # This static method to can orchastrate between "__init__" as it normal method and "create_indexing_of_collection" as it's async method
    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        # Create indexings if it's first time to create the collection
        await instance.create_indexing_of_collection()

        return instance


    # A method to create the indexing of the collection once the collection created
    async def create_indexing_of_collection(self):
        # Get all existing collections' names in mongodb
        all_collections = await self.db_client.list_collection_names()

        # Check if our collection already exist or not
        if DataBaseEnums.COLLECTION_DATA_CHUNK.value not in all_collections:
            # Iterate though all indexings in "DataChunk" schema
            for index in DataChunk.get_indexes(): # get_indexes returns all required indexings
                # Create the index
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )


    # A method to insert on chunk into database
    async def insert_chunk(self, chunk: DataChunk):
        
        # Insert the "chunk" into mongodb collection
        result = await self.collection.insert_one(chunk.model_dump())

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


