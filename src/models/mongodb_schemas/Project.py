from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson import ObjectId


# This class to validate the keys of project collection in mongodb
class Project(BaseModel):
    # This _id create by defualt in mongodb collections and has a special type called "ObjectId"
    # Note that "ObjectId" is not recognized by pydantic so we will handle it later
    _id: Optional[ObjectId]

    # Validate the project_id with type "str" and min_length = 2
    project_id: str = Field(..., min_length=2)

    # Handle the unknown type(ObjectId) by pydantic
    class Config:
        arbitrary_types_allowed = True

    # Adding extra custom validator to project_id to check it's alphanumeric
    @field_validator("project_id")
    def validate_is_alphnum(cls, value:str):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        
        return value