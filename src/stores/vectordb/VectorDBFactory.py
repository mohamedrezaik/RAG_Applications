from ...controllers import BaseController
from .VectorDBEnums import VectorDBNameEnums
from .providers import QdrantDBProvider

class VectorDBFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def ge_provider(self, provider: str):
        if provider == VectorDBNameEnums.QDRANT.value:
            db_path = self.base_controller.get_vecoterdb_path(db_name=self.config.VECTORDB_NAME)

            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTORDB_DISTANCE_METHOD
            )
        
        
        # If no provider setted
        return None