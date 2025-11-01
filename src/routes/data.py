from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings, DataValidation
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal, ProjectDataModel, ChunkDataModel, AssetDataModel, Asset, DataChunk, AssetTypeEnums
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
    project_data_model = await ProjectDataModel.get_instance(
        # We can access the variables within our "app" in main module by "Request" from fastapi
        db_client=request.app.database_conn
        )
    
    # Get "project_id" data from our database
    project = await project_data_model.get_project(project_id=project_id)

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

    # Insert the file details into assets collection in database
    # Get the "asset_data_model" to can process on assets collection in mongodb
    asset_data_model = await AssetDataModel.get_instance(
        # We can access the variables within our "app" in main module by "Request" from fastapi
        db_client=request.app.database_conn
        )
    
    # 
    asset_resource = Asset(
        asset_project_id=project._id,
        asset_type=AssetTypeEnums.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path),
        )
    
    asset_resource = await asset_data_model.insert_asset(asset=asset_resource)

    return JSONResponse(
         content={
             "signal": validate_signal,
             "file_id": str(asset_resource._id)
         }
    )
       

# This router to process uploaded data files
@data_router.post("/process/{project_id}")
async def process_files(request: Request, project_id:str, recieved_data:DataValidation): # We use 'DataValidation' as 'recieved_data' type to make FastApi deal with it as an object inhirets from pydantic 'BaseModel' to validate recieved data

    # Extract processing parameters from user request
    file_id = recieved_data.file_id
    chunk_size = recieved_data.chunk_size
    chunk_overlap = recieved_data.chunk_overlap
    do_reset = recieved_data.do_reset

    
    # Get an instance of "ProjectDataModel" to can deal with mongodb projects collection
    project_collection = await ProjectDataModel.get_instance(db_client=request.app.database_conn)

    # Validate the "project_id" exists in mongodb or not if not create project with this specific "project_id"
    project = await project_collection.get_project(project_id=project_id)

    # Get an instance of "ChunkDataModel" to can deal with mongodb data chunks collection
    data_chunk_collection = await ChunkDataModel.get_instance(db_client=request.app.database_conn)

    # Get the project_id files directory
    project_files_path = ProjectController().get_project_path(project_id=project_id)

    # Get an object to can processes on the requested project_id
    process_controller = ProcessController(project_path=project_files_path)

    # Get the "asset_data_model" to can process on assets collection in mongodb
    asset_data_model = await AssetDataModel.get_instance(
        # We can access the variables within our "app" in main module by "Request" from fastapi
        db_client=request.app.database_conn
        )
    if file_id:
        # Get the details of this file from mongodb as "Asset" type
        asset = await asset_data_model.get_one_asset(
            asset_project_id=project._id,
            asset_name=file_id,
        )

        # Check if the file not exist
        if asset is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_NOT_FOUND.value,
                }
            )
        
        project_file_ids = {asset._id: asset.asset_name}

    else:
        # Get all assets names of requested project as list of "Asset" type
        assets_details = await asset_data_model.get_all_assets(
            asset_project_id=project._id,
            asset_type=AssetTypeEnums.FILE.value,
        )

        # Get all file name in one list
        project_file_ids = {
            # asset_id (_id of the file in mongodb) and asset_name (file_id of the file in mongodb) as key and value
            asset._id: asset.asset_name
            for asset in assets_details
        }

        # Check if there is no files in the requested project
        if len(project_file_ids) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_PROCESS_FAILED.value,
                }
                )

    # Check if should to clear all past chunks data in mongodb of requested project
    if do_reset:
        _ = await data_chunk_collection.delete_chunks_by_project_id(project_id=project._id)

    # Iterate though all file_ids of the requested project
    inserted_chunks = 0
    no_files = 0
    for _id, file_id in project_file_ids.items():
        # Get file content
        file_content = process_controller.get_file_content(file_id=file_id)

        # Check if there is no file content (file_id not exist in disk)
        if file_content is None:
            logger.error(f"Error while processing this file id : {file_id}")
            continue

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
        

        # Convert the file_chunks list contents from "Document" type inot "DataChunk" type
        file_chunks = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_project_id=project._id, # This project id created by mongodb itself "_id"
                chunk_asset_id=_id
            )
            for i, chunk in enumerate(file_chunks)
        ]

        # Insert our chunks as batches into mongodb data chunks collection
        inserted_chunks += await data_chunk_collection.insert_batch_chunks(file_chunks)
        # Add another processed file to counter
        no_files += 1


    # Return number of inserted chunks
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESS_SUCCEEDED.value,
            "inserted_chunks": inserted_chunks,
            "processed_files": no_files,
        }
        )
