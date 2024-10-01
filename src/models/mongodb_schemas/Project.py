from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson import ObjectId



# This class to validate the keys of project collection in mongodb
class Project(BaseModel):
    # Handle the unknown type(ObjectId) by pydantic
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # This _id create by defualt in mongodb collections and has a special type called "ObjectId"
    # Note that "ObjectId" is not recognized by pydantic so we handled it using "ConfigDict(arbitrary_types_allowed=True)"
    _id: Optional[ObjectId]

    # Validate the project_id with type "str" and min_length = 1
    project_id: str = Field(..., min_length=1)


    # Adding extra custom validator to project_id to check it's alphanumeric
    @field_validator("project_id")
    def validate_is_alphnum(cls, value:str):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        
        return value