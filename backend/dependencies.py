from fastapi import UploadFile, HTTPException
from config import settings
from models import ExcelFileUpload
import os

async def validate_file_upload(file: UploadFile) -> ExcelFileUpload:
    """Validate uploaded file meets requirements"""
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1][1:].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE//(1024*1024)}MB"
        )
    
    return ExcelFileUpload(
        filename=file.filename,
        content_type=file.content_type,
        file_size=file.size
    )