from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os
# This class to perform required operations on Data uploading
class DataController(BaseController): # Inherit the general information from BaseController

    def __init__(self):
        super().__init__()
        # Initializing the scale to convert from MB INTO BYTES
        self.file_size_scale = 1048576 

    def validate_uploaded_file(self, file:UploadFile):

        # Validating file on our criterias
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * self.file_size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_UPLOAD_SUCCEED.value
    
    # A function to create a unique file name after cleaning the original file name to make sure it's writable and readable on the disk
    # It returns the file_path and new unique file name as an ID
    def generate_unique_file_path(self, orig_file_name:str, project_files_path:str):
        
        # Get a random key string to make our file name unique
        random_key = self.generate_random_string()

        # Get the cleaned version of original file name
        cleaned_file_name = self.clean_file_name(orig_file_name=orig_file_name)

        # Create a new file name to get a unique file name and make sure it's readable and writable on the disk
        new_file_name = random_key + "_" + cleaned_file_name

        # Concate new_file_name with project_files_path using 'os' lib to make it works with any machine type (linux, windowns, ...ect)
        file_path = os.path.join(
            project_files_path,
            new_file_name
        )

        # Check new_file_name is unique in the project files dir (otherwise work still get unique one)
        while os.path.exists(file_path):
            random_key = self.generate_random_string()
            new_file_name = random_key + "_" + cleaned_file_name
            file_path = os.path.join(
            project_files_path,
            new_file_name
            )

        return file_path, new_file_name

    def clean_file_name(self, orig_file_name:str):

        # Replace any whitel space with '_'
        cleaned_file_name = orig_file_name.replace(" ", "_")

        # Remove any special characters, except '_' and '.'
        cleaned_file_name = re.sub(r"[^\w.]", "", cleaned_file_name)

        return cleaned_file_name