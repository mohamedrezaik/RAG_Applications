from fastapi import FastAPI

# Create FastApi object
app = FastAPI()

# Create gate function to be accessed by api requests
@app.get("/dev")
def welcome():
    return {
        "message": "Hello world!"
    }