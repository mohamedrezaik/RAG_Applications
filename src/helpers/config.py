from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # Set and Validate the environment variables to access and manage theme
    APP_NAME: str # Validate it's string type
    APP_VERSION: str # Validate it's string type

    FILE_ALLOWED_TYPES: list # Validate it's list type
    FILE_MAX_SIZE: int # Validate it's int type
    FILE_DEFAULT_CHUNK_SIZE: int # Validate it's int type

    # Mongo connection variables
    MONGODB_DATABASE: str
    MONGODB_URL: str

    class Config:
        # Setting the environment variables file name
        env_file = ".env"

# A function to get an object of settings (it enables us to access environment variables)
def get_settings():
    return Settings()