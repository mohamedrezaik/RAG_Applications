from helpers import get_settings

# This class has general configurations to be inhirated to models related to database
class BaseDataModel:

    def __init__(self, db_client):
        # Our connection to database
        self.db_client = db_client 

        # Settings to access environment settings
        self.settings = get_settings()