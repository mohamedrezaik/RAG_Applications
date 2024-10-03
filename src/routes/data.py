from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings, DataValidation
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal, ProjectDataModel, ChunkDataModel, DataChunk
from aiofile import async_open
import os
import logging

# Create a logger to log the system errors under 'uvicorn.error' tag
logger = logging.getLogger(name="uvicorn.error")


# Create the data loader router
data_router = APIRouter(
    prefix="/api/v1/data", # Adding this prefix for all routes Links
    tags=["api_v1", "data"]
)

# This router to upload data files
@data_router.post("/upload/{project_id}") # project_id to direct the user into desired operations
async def upload_data(
                    request: Request,
                    project_id:str,
                    file:UploadFile, # We use UploadFile from fastapi to recieve the user files via it to allow fastapi deals with it probably
                    app_settings:Settings=Depends(get_settings), # We set the settings type as Settings class and use Depends from FastAPI to be sure get_settings() works probably
                    ):
    
    # Get the "project_data_model" to can process on projects collection in mongodb
    project_data_model = ProjectDataModel(
        # We can access the variables within our "app" in main module by "Request" from fastapi
        db_client=request.app.database_conn
        )
    
    # Get all "project_id" data from our database
    project_id_info, total_pages = await project_data_model.get_all_projects()

    # Create an object of DataController to can operate on recieved data
    data_controller = DataController()

    # Validating the file properties
    is_valid, validate_signal = data_controller.validate_uploaded_file(file=file)
    
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
    project_files_path = ProjectController().get_project_path(project_id=project_id)

    # Create a file_path and a file_id for the recieved file inside project files dir
    file_path, file_id = data_controller.generate_unique_file_path(
        orig_file_name=file.filename, 
        project_files_path=project_files_path
        )
    
    # We create a try and except here because accessing and writing on disk have some risks that may occur
    try:
        # Read chuck by chunk from sent file then Write chunck by chunck in project_id files directory(file_path)
        async with async_open(file_path, "wb") as f:
            while chunk := await file.read(size=app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        # Log the error in the system not to users
        logger.error(f"File uploading error: {e}")
        
        # User oriented response not the error details
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )


    return JSONResponse(
         content={
             "signal": validate_signal,
             "file_id": file_id
         }
    )
       

# This router to process uploaded data files
@data_router.post("/process/{project_id}")
async def process_files(request: Request, project_id:str, recieved_data:DataValidation): # We use 'DataValidation' as 'recieved_data' type to make FastApi deal with it as an object inhirets from pydantic 'BaseModel' to validate recieved data

    # Extract processing parameters from user request
    chunk_size = recieved_data.chunk_size
    chunk_overlap = recieved_data.chunk_overlap
    do_reset = recieved_data.do_reset

    
    # Get an instance of "ProjectDataModel" to can deal with mongodb projects collection
    project_collection = ProjectDataModel(db_client=request.app.database_conn)

    # Validate the "project_id" exists in mongodb or not if not create project with this specific "project_id"
    project = await project_collection.get_project(project_id=project_id)

    # Get an instance of "ChunkDataModel" to can deal with mongodb data chunks collection
    data_chunk_collection = ChunkDataModel(db_client=request.app.database_conn)

    # Get the project_id files directory
    project_files_path = ProjectController().get_project_path(project_id=project_id)

    # Get an object to can processes on the requested project_id
    process_controller = ProcessController(project_path=project_files_path)

    # Get file content
    file_content = process_controller.get_file_content(file_id=recieved_data.file_id)

    # Get file content as chuncks
    file_chunks = process_controller.get_file_chunks(file_content=file_content, 
                                                      chunk_size=chunk_size, 
                                                      chunk_overlap=chunk_overlap)
    
    # Check if chunking succeeded or not
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESS_FAILED.value
            }
        )
    
    if do_reset:
        _ = await data_chunk_collection.delete_chunks_by_project_id(project_id=project._id)

    # Convert the file_chunks list contents from "Document" type inot "DataChunk" type
    file_chunks = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project._id # This project id created by mongodb itself "_id"
        )
        for i, chunk in enumerate(file_chunks)
    ]

    # Insert our chunks as batches into mongodb data chunks collection
    inserted_chunks = await data_chunk_collection.insert_batch_chunks(file_chunks)


    # Return number of inserted chunks
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_SUCCEEDED.value,
            "inserted_chunks": inserted_chunks
        }
        )
