from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class ApiConfig(BaseModel):
    anthropicApiKey: Optional[str] = None
    openaiApiKey: Optional[str] = None
    preferredProvider: str = "anthropic"

class ContentIdea(BaseModel):
    id: str
    title: str
    description: str

class VideoScript(BaseModel):
    id: str
    ideaId: str
    title: str
    script: str

class LinkedInPost(BaseModel):
    id: str
    scriptId: str
    post: str

class ApiRequest(BaseModel):
    anthropicApiKey: Optional[str] = None
    openaiApiKey: Optional[str] = None
    preferredProvider: str = "anthropic"
    transcript: Optional[str] = None
    instructions: Optional[str] = ""
    idea: Optional[ContentIdea] = None
    script: Optional[VideoScript] = None

class ApiResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

class TestConnectionResponse(BaseModel):
    success: bool
    provider: Optional[str] = None
    message: str
    error: Optional[Any] = None