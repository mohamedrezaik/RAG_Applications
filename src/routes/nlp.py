from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings, NLPValidation
from models import ProjectDataModel, ChunkDataModel, ResponseSignal
from controllers import NLPController

import logging
logger = logging.getLogger("uvicorn.error")

# Create nlp route
nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: NLPValidation):
    
    project_model = await ProjectDataModel.get_instance(
        db_client= request.app.database_conn
    )
    
    project = await project_model.get_project(
        project_id=project_id
    )
    
    chunk_model = await ChunkDataModel.get_instance(
        db_client=request.app.database_conn
    )
    
    nlp_controller = NLPController(
        vectordb_provider=request.app.vectordb_provider,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client
    )
    
    page = 1
    inserted_count = 0
    idx = 0
    
    while True:
        chunks = await chunk_model.get_project_chunks(project_id=project._id, page_no=page)
        
        # Exit if there is no data
        if not chunks or len(chunks) == 0:
            break
        
        # Create id for each chunk
        chunks_ids = list(range(idx, idx + len(chunks)))
        idx += len(chunks)
        
        is_inserted = nlp_controller.insert_into_vectordb(
            project=project,
            chunks=chunks,
            chunks_ids=chunks_ids,
            do_rest=push_request.do_reset
            )
        
        if not is_inserted:
            return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
            }
        )
        
        inserted_count += len(chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCEEDED.value,
            "inserted_items_count": inserted_count
        }
    )
        
        
    
    
    
    