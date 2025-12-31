from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnums
from .db_schemas import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne # Operation type(insert on record)
from sqlalchemy import func, delete
from sqlalchemy.future import select

class ChunkDataModel(BaseDataModel):

    def __init__(self, db_client: object):
        # Make the parent (BaseDataModel) see the db_client
        super().__init__(db_client=db_client)

        self.db_client = db_client

    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        
        return instance


    # A method to insert on chunk into database
    async def insert_chunk(self, chunk: DataChunk):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
            
        return chunk

    # A method to get a specific chunk from mongodb collection
    async def get_chunk(self, chunk_id: str):
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
                data_chunk = result.scalar_one_or_none()
                
                    
                return data_chunk
        
    
    # A method to get all chunks of a specific project
    async def get_project_chunks(self, project_id: ObjectId, page_no: int=1, page_size: int=50):
        async with self.db_client() as session:
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no-1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()
        
        return records
        

    # A method to insert chunks as batchs(it's more efficient to insert large number of chunks(instead of one by one) for our database)
    async def insert_batch_chunks(self, chunks: list, batch_size: int=100):
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i: i+batch_size]
                    session.add_all(batch)
            await session.commit()
        
        return len(chunks)
       
    
    # A method to delete the chunks of a specific project with "project_id" from mognodb data collection
    async def delete_chunks_by_project_id(self, project_id: ObjectId):

        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        
        return result.rowcount()


