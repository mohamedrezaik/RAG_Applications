from fastapi import FastAPI

# Loading all environment variables into the system and make them globally accessable by setting them in main.py
from dotenv import load_dotenv
load_dotenv(".env")

from routes import base

# Create FastApi object
app = FastAPI()

# Adding the base route to our app
app.include_router(base.base_router)