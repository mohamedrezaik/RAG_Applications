from enum import Enum

class VectorDBNameEnums(Enum):
    QDRANT: str = "QDRANT"


class DistanceMethodEnums(Enum):
    # Similarity Measurements
    COSINE: str = "cosine"
    DOT: str = "dot"