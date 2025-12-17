from .BaseController import BaseController
import os
# This class to perform general required operations for the project
class ProjectController(BaseController): # Inherit the general information from BaseController

    def __init__(self):
        super().__init__()

    # This function to return the requested project_id files directory 
    def get_project_path(self, project_id:int):

        # We use 'os' library to get the direcotry of our project_id files in a stable way and work on any machine(linux, windows, ...ect)
        project_dir = os.path.join(
            self.file_dir, # The files base directory of all projects files directories
            project_id # Adding the specific requested project_id
        )

        # Check if the directory of project_id files existing
        if not os.path.exists(project_dir):
            # If not exist, create it
            os.makedirs(project_dir)
        
        # Finally return the project_id files directory
        return project_dir