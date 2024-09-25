from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

# Create the default router
base_router = APIRouter(
    prefix="/app/v1", # Adding this prefix for all routes Links
    tags=["api_v1"]
)

# Create the default function responsible for default response(app name and version)
@base_router.get("/")
async def default_fun(
    # Loading env variables using our config module
    settings:Settings=Depends(get_settings), # We set the settings type as Settings class and use Depends from FastAPI to be sure get_settings() works probably
    ):
    # Loading env variables
    app_name = settings.APP_NAME
    app_version = settings.APP_VERSION

    return {
        "APP_NAME": app_name,
        "APP_VERSION": app_version
    }