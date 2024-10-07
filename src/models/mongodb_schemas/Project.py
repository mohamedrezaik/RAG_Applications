from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId



# This class to validate the keys of project collection in mongodb
class Project(BaseModel):
    # Handle the unknown type(ObjectId) by pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # This _id create by defualt in mongodb collections and has a special type called "ObjectId"
    # Note that "ObjectId" is not recognized by pydantic so we handled it using "ConfigDict(arbitrary_types_allowed=True)"
    # We have to access it directly because it's private property like this (DataChunk._id)
    _id: Optional[ObjectId]

    # Validate the project_id with type "str" and min_length = 1
    project_id: str = Field(..., min_length=1)


    # Adding extra custom validator to project_id to check it's alphanumeric
    @field_validator("project_id")
    def validate_is_alphnum(cls, value:str):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        
        return value
    
    # A method to get the indexing parameters for all indexings
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("project_id", 1)], # 1 refers to the ordering technique (ascending)
                "name": "project_id_index_1", # Name of indexing
                "unique": True # Refers to the values in "project_id" must be unique
            },
        ]