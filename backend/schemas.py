from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from models import TaskStatus

class ProcessedDataResponse(BaseModel):
    status: TaskStatus
    message: str = Field(..., example="File processed successfully")
    data: List[Dict[str, Any]]
    warnings: Optional[List[str]] = None
    errors: Optional[List[str]] = None

class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str]
    result: Optional[Dict[str, Any]] = None

class FileUploadResponse(BaseModel):
    task_id: str
    message: str = Field(default="File uploaded successfully")
    file_info: Dict[str, Any]
    
class ErrorResponse(BaseModel):
    error: str = Field(..., example="Invalid file format")
    details: Optional[str] = None
    error_code: Optional[int] = None