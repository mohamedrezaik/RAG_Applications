from pydantic import BaseModel
from typing import Optional

# Building our nlp schema
# This class can help us to validate these nlp request data to be ensure it follows our data schema
class NLPValidation(BaseModel):
    # We used 'do' to define it as a requested operation. it requests to clear all processed files or not
    do_reset: Optional[bool] = False 