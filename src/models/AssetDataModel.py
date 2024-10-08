from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnums
from .mongodb_schemas import Asset
from bson.objectid import ObjectId
from pymongo import InsertOne # Operation type(insert on record)


class AssetDataModel(BaseDataModel):

    def __init__(self, db_client: object):
        # Make the parent (BaseDataModel) see the db_client
        super().__init__(db_client)

        # Get the data chunk collection
        self.collection = self.db_client[DataBaseEnums.COLLECTION_ASSET_NAME.value]

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
        if DataBaseEnums.COLLECTION_ASSET_NAME.value not in all_collections:
            # Iterate though all indexings in "DataChunk" schema
            for index in Asset.get_indexes(): # get_indexes returns all required indexings
                # Create the index
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    # A method to insert an asset into database
    async def insert_asset(self, asset: Asset):
        
        # Insert the "asset" into mongodb collection
        result = await self.collection.insert_one(asset.model_dump())

        # Store the mongodb "_id" into our chunk
        asset._id = result.inserted_id

        return asset
    
    # A method to get all asset details by asset_project_id
    async def get_all_assets_by_project_id(self, asset_project_id: str):
        # Return all assets associated with requested asset_project_id
        return await self.collection.find(
            {
                "asset_project_id": ObjectId(asset_project_id)
            }
        ).to_list(length=None)
