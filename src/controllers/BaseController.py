from helpers.config import get_settings, Settings
import os

class BaseController:
    # Initializing the general settings to be inherited with BaseController class as a general knowledge in this module
    def __init__(self):
        self.app_settings: Settings = get_settings()

        # This code to get automatically the base directory of this module using dynamic code that can work on any machine(linux, windows,...ect)
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

        # Get the file directory (location of uploaded user's files) automatically and stable to work on any machine type using 'os' library
        self.file_dir = os.path.join(
            self.base_dir, # We used the self.base_dir as a parent dir because it's common to access files dir
            "assets",
            "files"
        )