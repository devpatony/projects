import pandas as pd
import re
import os
import logging
from typing import Tuple
from models import ValidationResult
from flask import jsonify

class ValidationService:
    MANDATORY_COLUMNS = [
        'Employee Name',
        'Email', 
        'Phone Number',
        'Employment Type',
        'Gender'
    ]
    
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_REGEX = r'^\+?[\d\s-]{10,15}$'
    
    @classmethod
    def validate_mandatory_columns(cls, df: pd.DataFrame) -> ValidationResult:
        missing = [col for col in cls.MANDATORY_COLUMNS if col not in df.columns]
        return ValidationResult(
            is_valid=not missing,
            message=f"Missing columns: {', '.join(missing)}" if missing else "All columns present",
            missing_columns=missing
        )
    
    @classmethod
    def validate_data(cls, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        errors = []
        df_clean = df.copy()
        
        # Email validation
        if 'Email' in df.columns:
            invalid_emails = df[~df['Email'].astype(str).str.match(cls.EMAIL_REGEX, na=False)]
            if not invalid_emails.empty:
                errors.append(f"{len(invalid_emails)} invalid emails")
        
        # Phone validation
        if 'Phone Number' in df.columns:
            invalid_phones = df[~df['Phone Number'].astype(str).str.match(cls.PHONE_REGEX, na=False)]
            if not invalid_phones.empty:
                errors.append(f"{len(invalid_phones)} invalid phone numbers")
        
        return df_clean, errors

def process_file(filepath: str, df: pd.DataFrame):
    logging.info(f"File received: {os.path.basename(filepath)}")
    logging.info(f"File saved to: {filepath}")
    
    validation_result = ValidationService.validate_mandatory_columns(df)
    logging.info(f"Validation result: {validation_result}")
    
    if not validation_result.is_valid:
        os.remove(filepath)  # Cleanup the file
        return jsonify({
            "error": validation_result.message,
            "missing_columns": validation_result.missing_columns
        }), 400