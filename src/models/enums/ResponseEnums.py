from enum import Enum

# We define our constant responses with a class inhirets form Enum class to have its properties
class ResponseSignal(Enum):

    # Defining our constants responses to be used in many situations
    FILE_TYPE_NOT_SUPPORTED: str = "FILE_TYPE_NOT_SUPPORTED"
    FILE_SIZE_EXCEEDED: str = "FILE_SIZE_EXCEEDED"
    FILE_VALIDATE_SUCCEEDED: str = "FILE_VALIDATE_SUCCEEDED"
    FILE_UPLOAD_SUCCEEDED: str = "FILE_UPLOAD_SUCCEEDED"
    FILE_UPLOAD_FAILED: str= "FILE_UPLOAD_FAILED"

    PROCESS_FAILED: str = "PROCESS_FAILED"
    PROCESS_SUCCEEDED: str = "PROCESS_SUCCEEDED"

    MONGODB_CONNECTION_FAILED: str= "MONGODB_CONNECTION_FAILED"

