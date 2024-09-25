from fastapi import FastAPI, APIRouter
import os

# Create the default router
base_router = APIRouter(
    prefix="/app/v1" # Adding this prefix for all routes Links
)

# Create the default function responsible for default response(app name and version)
@base_router.get("/")
async def default_fun():
    # Loading env variables from the system
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")

    return {
        "APP_NAME": app_name,
        "APP_VERSION": app_version
    }