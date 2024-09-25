from helpers.config import get_settings, Settings


class BaseController:
    # Initializing the general settings to be inherited with BaseController class as a general knowledge in this module
    def __init__(self):
        self.app_settings: Settings = get_settings()