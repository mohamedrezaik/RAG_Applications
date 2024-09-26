from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController


# Create the data loader router
base_router = APIRouter(
    prefix="/api/v1/data", # Adding this prefix for all routes Links
    tags=["api_v1", "data"]
)

@base_router.post("/upload/{project_id}") # project_id to direct the user into desired operations
async def upload_data(
                    project_id:str,
                    file:UploadFile, # We use UploadFile from fastapi to recieve the user files via it to allow fastapi deals with it probably
                    settings:Settings=Depends(get_settings), # We set the settings type as Settings class and use Depends from FastAPI to be sure get_settings() works probably
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

    # If it's valide return good response    
    return JSONResponse(
         status_code = status.HTTP_200_OK,
         content={
             "signal": validate_signal
         }
    )
       