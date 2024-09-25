from fastapi import FastAPI, APIRouter

# Create the default router
base_router = APIRouter()

# Create the default function responsible for default response
base_router.get("/")
def default_fun():
    return {
        "message": "Welcome!"
    }