from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROGRESS = "PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class ExcelProcessingTask(BaseModel):
    task_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    status: TaskStatus
    progress: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str] = Field(None, example="Processing row 100/500")
    result: Optional[List[Dict[str, Any]]] = None

class ExcelFileUpload(BaseModel):
    filename: str = Field(..., example="employees.xlsx")
    content_type: str = Field(..., example="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    file_size: int = Field(..., example=10240)

class ValidationResult(BaseModel):
    is_valid: bool
    message: str = Field(..., example="Missing required columns")
    missing_columns: List[str] = Field(default_factory=list)
    invalid_rows: Optional[List[int]] = None