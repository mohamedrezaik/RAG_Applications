from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId
from datetime import datetime

# This class to validate the keys of assets collection in mongodb
class Asset(BaseModel):
    # Handle the unknown type(ObjectId) by pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # This _id create by defualt in mongodb collections and has a special type called "ObjectId"
    # Note that "ObjectId" is not recognized by pydantic so we handled it above
    # We have to access it directly because it's private property like this (Asset._id)
    _id: Optional[ObjectId]
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: Optional[dict] = Field(default=None)
    asset_created_date: datetime = Field(default=datetime.utcnow())

    # A method to get the indexing parameters for all indexings
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_project_id", 1)], # 1 refers to the ordering technique (ascending)
                "name": "asset_project_id_index_1", # Name of indexing
                "unique": False # Refers to the values in "asset_project_id" is not unique
            },
            {
                "key": [("asset_project_id", 1), ("asset_name", 1)], # 1 refers to the ordering technique (ascending)
                "name": "asset_project_id_name_index_1", # Name of indexing
                "unique": True # Refers to the values in combination "asset_project_id" and "asset_name" are unique
            },
        ]
