from .BaseController import BaseController
from fastapi import UploadFile

# This class to perform required operations on Data uploading
class DataController(BaseController): # Inherit the general information from BaseController

    def __init__(self):
        super().__init__()
        # Initializing the scale to convert from MB INTO BYTES
        self.file_size_scale = 1048576 

    def validate_uploaded_file(self, file:UploadFile):

        # Validating file on our criterias
        if (file.content_type not in self.app_settings.FILE_ALLOWED_TYPES) or (file.size > self.app_settings.FILE_MAX_SIZE * self.file_size_scale):
            return False
        
        return True