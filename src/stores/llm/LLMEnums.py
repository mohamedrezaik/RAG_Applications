from enum import Enum

class LLMEnums(Enum):
    OPENAI: str = "OPENAI"
    COHERE: str = "COHERE"

class OpenAIEnums(Enum):

    SYSTEM: str = "system"
    USER: str = "user"
    ASSISTANT: str = "assistant"

class CoHereEnums(Enum):

    SYSTEM: str = "SYSTEM"
    USER: str = "USER"
    ASSISTANT: str = "CHATBOT"

    DOCUMENT: str = "search_document"
    QUERY: str = "search_query"

class DocumentTypeEnums(Enum):

    DOCUMENT: str = "Document"
    QUERY: str = "Query"