from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes import base
from routes import data

from motor.motor_asyncio import AsyncIOMotorClient # This for creating a mongo engine connected to monodb server

from helpers import config

import logging

# Create a logger to log the system errors under 'uvicorn.error' tag
logger = logging.getLogger(name="uvicorn.error")


# This function will be fired once when the application start and shutdown
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

    yield # Before shutdown the applicaton to the following
    app.mongodb_client.close()

# Create FastApi object
app = FastAPI(lifespan=lifespan)


# Adding the base route to our app
app.include_router(base.base_router)

# Adding the data route to our app
app.include_router(data.data_router)