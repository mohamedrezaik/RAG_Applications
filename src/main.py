from fastapi import FastAPI
from routes import base
from routes import data
# Create FastApi object
app = FastAPI()

# Adding the base route to our app
app.include_router(base.base_router)

# Adding the data route to our app
app.include_router(data.base_router)