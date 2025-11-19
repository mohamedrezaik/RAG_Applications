from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base, data, nlp
from stores import LLMProvidersFactory
from stores import VectorDBFactory
from stores.llm.templates.templates_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from helpers import config

import logging

# Create a logger to log the system errors under 'uvicorn.error' tag
logger = logging.getLogger(name="uvicorn.error")


# This function will be fired once the application starts or shutdowns
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Get the settings to extract dependencies of mongo connection(Environment variables)
    settings = config.get_settings()

    # Get Postgres connection details from environment variables
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    # Create the db_engine and connection to database inside 'app' to be accessed any where
    app.db_engine = create_async_engine(postgres_conn)
    app.database_conn = sessionmaker(
        app.db_engine, expire_on_commit=False, class_=AsyncSession
    )

    # Get the LLM providers Factory
    llm_provider_factory = LLMProvidersFactory(settings)
    
    # Get the vectordb provider Factory
    vectordb_provider_factory = VectorDBFactory(settings)

    # Set the generation provider in "app"
    app.generation_client = llm_provider_factory.ge_provider(provider=settings.GENERATION_PROVIDER)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Set the Embedding provider in "app"
    app.embedding_client = llm_provider_factory.ge_provider(provider=settings.EMBEDDING_PROVIDER)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE) 

    # Set the vectordb provider in "app"
    app.vectordb_provider = vectordb_provider_factory.ge_provider(provider=settings.VECTORDB_PROVIDER)
    # Connect to the vectordb 
    app.vectordb_provider.connect()
    
    # Define template parser of required language
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
        )
    
    yield # Before shutdown the applicaton do the following
    # Close db_engine connection
    await app.db_engine.dispose()
    # Close vectordb connection
    app.vectordb_provider.disconnect()
    

# Create FastApi object
app = FastAPI(lifespan=lifespan)


# Adding the base route to our app
app.include_router(base.base_router)

# Adding the data route to our app
app.include_router(data.data_router)

# Adding the nlp route to our app
app.include_router(nlp.nlp_router)