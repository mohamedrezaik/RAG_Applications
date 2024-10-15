from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base
from routes import data
from stores import LLMProvidersFactory
from motor.motor_asyncio import AsyncIOMotorClient # This for creating a mongo engine connected to monodb server

from helpers import config

import logging

# Create a logger to log the system errors under 'uvicorn.error' tag
logger = logging.getLogger(name="uvicorn.error")


# This function will be fired once the application starts or shutdowns
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Get the settings to extract dependencies of mongo connection(Environment variables)
    settings = config.get_settings()

    # Get mongodb URL and mongodb name
    mongodb_url = settings.MONGODB_URL
    mongodb_database = settings.MONGODB_DATABASE

    # Create the mongodb client and connection to database inside 'app' to be accessed any where
    app.mongodb_client = AsyncIOMotorClient(mongodb_url)
    app.database_conn = app.mongodb_client[mongodb_database]

    # Get the LLM providers Factory
    llm_provider_factory = LLMProvidersFactory(settings)

    # Set the generation provider in "app"
    app.generation_client = llm_provider_factory.ge_provider(provider=settings.GENERATION_PROVIDER)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Set the Embedding provider in "app"
    app.embedding_client = llm_provider_factory.ge_provider(provider=settings.EMBEDDING_PROVIDER)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE) 

    yield # Before shutdown the applicaton do the following
    app.mongodb_client.close()

# Create FastApi object
app = FastAPI(lifespan=lifespan)


# Adding the base route to our app
app.include_router(base.base_router)

# Adding the data route to our app
app.include_router(data.data_router)