from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from aiofile import async_open
import os

# Create the data loader router
base_router = APIRouter(
    prefix="/api/v1/data", # Adding this prefix for all routes Links
    tags=["api_v1", "data"]
)

@base_router.post("/upload/{project_id}") # project_id to direct the user into desired operations
async def upload_data(
                    project_id:str,
                    file:UploadFile, # We use UploadFile from fastapi to recieve the user files via it to allow fastapi deals with it probably
                    app_settings:Settings=Depends(get_settings), # We set the settings type as Settings class and use Depends from FastAPI to be sure get_settings() works probably
                    ):
    
    # Validating the file properties
    is_valid, validate_signal = DataController().validate_uploaded_file(file=file)
    
    # Check if the file not valid
    if not is_valid:
        # Return an object type of JSONResponse from fastapi.responses to be standard with api responses
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal": validate_signal
            }
        )

    # If it's valid

    # Get the project_id files directory
    project_files_dir = ProjectController().get_project_path(project_id=project_id)

    # Create a file_path of recieved file inside project_files_dir
    file_path = os.path.join(
        project_files_dir,
        file.filename
    )
    # Read chuck by chunk from sent file then Write chunck by chunck in project_id files directory(file_path)
    async with async_open(file_path, "wb") as f:
        while chunk := await file.read(size=app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)
    

    return JSONResponse(
         content={
             "signal": validate_signal,
             "project_dir": project_files_dir
         }
    )
       