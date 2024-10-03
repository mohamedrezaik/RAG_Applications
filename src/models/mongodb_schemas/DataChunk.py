from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson import ObjectId


# This class to validate the keys of data chunks collection in mongodb
class DataChunk(BaseModel):
    # Handle the unknown type(ObjectId) by pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # This _id create by defualt in mongodb collections and has a special type called "ObjectId"
    # Note that "ObjectId" is not recognized by pydantic so we handled it above
    # We have to access it directly because it's private property like this (DataChunk._id)
    _id: Optional[ObjectId]

    # The minimum text length in chunk_text is 1
    chunk_text: str = Field(..., min_length=1)

    chunk_metadata: dict
    
    # The text length in chunk_order must be greater than 0
    chunk_order: int = Field(..., gt=0)

    # project id here refers to _id in "Project" module
    chunk_project_id: ObjectId
