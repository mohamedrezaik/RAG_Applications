from enum import Enum

# We define our constant responses with a class inhirets form Enum class to have its properties
class ResponseSignal(Enum):

    # Defining our constants responses to be used in many situations
    FILE_TYPE_NOT_SUPPORTED: str = "FILE_TYPE_NOT_SUPPORTED"
    FILE_SIZE_EXCEEDED: str = "FILE_SIZE_EXCEEDED"
    FILE_VALIDATE_SUCCEED: str = "FILE_VALIDATE_SUCCEED"
    FILE_UPLOAD_SUCCEED: str = "FILE_UPLOAD_SUCCEED"
    FILE_UPLOAD_FAILED: str= "FILE_UPLOAD_FAILED"
