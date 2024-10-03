from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnums
from .mongodb_schemas import Project


class ProjectDataModel(BaseDataModel):

    def __init__(self, db_client):
        # Make the parent (BaseDataModel) see the db_client
        super().__init__(db_client)

        # Get the collection of projects from our database
        self.collection = self.db_client[DataBaseEnums.COLLECTION_PROJECT_NAME.value]

    # This method to create a new document in projects collection
    # This method takes data in type of "Project" (inhiret from pydantic) to validate the data
    async def create_project_doc(self, project:Project):

        # Insert a new document and await it to get the result of insertion
        result = await self.collection.insert_one(project.model_dump()) # We used project.model_dump() to convert our validated variables into dictoinary formatting to be inserted in database

        # As any insertion operation in mongodb has "_id" so we can get it from result
        project._id = result.inserted_id
        
        # Our return be "Project" type
        return project
        
    # This method to get a specific document in project collection, if it's not exist create one
    async def get_project(self, project_id: str):
        
        # Get the document(dictionary formatting) of a specific "project_id"
        document = await self.collection.find_one({"project_id": project_id})
        
        # Check if the specific project document exists
        if document is None:

            # Create a new "Project" (inhirets from pydantic) to insert it as document
            project = Project(project_id=project_id)

            # Insert a new document with a specific "project_id"
            project = await self.create_project_doc(project)


            # Our return be "Project" type
            return project
        
        # Our return is "Project" type
        # Note: we assingned "_id" manually because it is dealed as private variable so we have to assign it explicitly
        project = Project(**document)
        project._id = document["_id"]

        return project
    
    # This method to return all project documents
    async def get_all_projects(self,pages:int=1, page_size: int=10):

        # Count total documents number
        total_doc_count = await self.collection.count_documents({})

        # Calculate number of required pages
        total_pages = total_doc_count // page_size
        if total_doc_count % page_size:
            total_pages += 1

        if total_pages == 0:
            # If there is no any documents in database
            return [], total_pages
        
        curser = self.collection.find({}).skip(((total_pages - pages) * page_size)).limit(pages * page_size)

        # Collect project documents in a list
        projects_doc = []
        async for doc in curser:
            # Create an object of "Project" type to validate our database keys
            # Note: we assingned "_id" manually because it is dealed as protected variable so we have to assign it explicitly
            project = Project(**doc)
            project._id = doc["_id"]
            projects_doc.append(
                project
                )

        return projects_doc, total_pages

            

