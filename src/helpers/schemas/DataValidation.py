from pydantic import BaseModel
from typing import Optional

# Building our data schema
# This class can help us to validate these data to be ensure it follows our data schema
class DataValidation(BaseModel):
    file_id: str
    chunk_size: Optional[int] = 100
    chunk_overlap: Optional[int] = 20
    # We used 'do' to define it as a requested operation. it requests to clear all processed files or not
    do_reset: Optional[bool] = False 