from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnums
from .db_schemas import Project
from sqlalchemy.future import select
from sqlalchemy import func

class ProjectDataModel(BaseDataModel):

    def __init__(self, db_client: object):
        # Make the parent (BaseDataModel) see the db_client
        super().__init__(db_client=db_client)

        self.db_client = db_client

    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        

        return instance



    # This method to create a new document in projects collection
    async def create_project_doc(self, project:Project):

        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
            
        return project
        
    async def get_project(self, project_id: int):
        
        async with self.db_client() as session:
            async with session.begin():
                result = await session.execute(select(Project).where(Project.project_id == project_id))
                project = result.scalar_one_or_none()
                if project is None:
                    project = await self.create_project_doc(Project(project_id=project_id))
            
        return project
        
    
    # This method to return all project documents
    async def get_all_projects(self,pages:int=1, page_size: int=10):

        async with self.db_client() as session:
            async with session.begin():
                total_documents = await session.execute(select(
                    func.count(Project.project_id)
                ))
                total_documents = total_documents.scalar_one()
                
                total_pages = total_documents // page_size
                if total_documents % page_size:
                    total_pages += 1
                    
                if total_pages == 0:
                    return [], total_pages
                    
                result = await session.execute(select(Project).offset((pages - 1) * page_size).limit(page_size))
                projects = result.scalars().all()

        return projects, total_pages


            

