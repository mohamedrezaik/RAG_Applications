from fastapi import FastAPI
from routes import base

# Create FastApi object
app = FastAPI()

# Adding the base route to our app
app.include_router(base.base_router)