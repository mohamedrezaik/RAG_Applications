from .BaseController import BaseController
import os
# We use these loaders from langchain to unify the use of these libraries in coding
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from models import ProcessEnums

# This class to use its properties in files processing
class ProcessController(BaseController):

    def __init__(self, project_path:str):
        super().__init__()
        self.project_path = project_path

    # Get file extention
    def get_file_extention(self, file_id:str):
        # Get the last value (file extention) from splitted text(file name)
        return os.path.splitext(file_id)[-1]
    
    # Get the file loader to can read it
    def get_file_loader(self, file_id:str):

        # Get the file_path
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        # Check if the file exists
        if not os.path.exists(file_path):
            return None

        # Get the file extention
        file_extention = self.get_file_extention(file_id=file_id)

        # Check if the file extention is ".txt" to use TxtLoader
        if file_extention == ProcessEnums.TXT.value:
            # Return plain text loader to read the content
            # We will use "utf-8" as an encoder to do not face issues with Arabic Langauge
            return TextLoader(file_path, encoding="utf-8") 
        
        # Check if the file extention is ".pdf" to use PyMuPDFLoader
        if file_extention == ProcessEnums.PDF.value:
            # Return plain text loader to read the content
            # We can set the parameter "extract_images" to True it's by default False
            return PyMuPDFLoader(file_path) 
        
        # If it's not within above extentions then return None
        return None

    # Get file content as a list of Documents
    def get_file_content(self, file_id:str):

        # Get the file loader the can we extract content from 
        loader = self.get_file_loader(file_id=file_id)

        # Check if the loader is empty(no file_id exists)
        if loader is None:
            return None

        # This will return a list contains "Documents contain content and metadata" for each page from the file
        return loader.load()
    
    # Get file content splitted into chunks(each chunk is a Document type)
    def get_file_chunks(self, file_content: list, chunk_size:int=100, chunk_overlap:int=20):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        # Set file content in a list
        pages_content = [
            doc.page_content
            for doc in file_content
        ]

        # Set file metadata in a list
        pages_metadata = [
            doc.metadata
            for doc in file_content
        ]
        

        # Split the text inot chunks (each chunk is a Document type that has content and metadata)
        file_chunks = text_splitter.create_documents(
            texts=pages_content,
            metadatas=pages_metadata
        )

        return file_chunks