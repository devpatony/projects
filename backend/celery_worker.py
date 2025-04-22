from celery import Celery
from config import settings
import pandas as pd
import os
import logging
from typing import Dict, Any
from services.validation_service import ValidationService

logging.basicConfig(level=logging.INFO)

celery = Celery(
    'tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery.task(bind=True)
def process_excel_task(self, filepath: str, task_id: str) -> Dict[str, Any]:
    logging.info(f"Task started for file: {filepath}, task_id: {task_id}")
    try:
        # Simulate processing
        self.update_state(state='PROGRESS', meta={'message': 'Processing file...'})
        logging.info("Processing file...")

        # Your actual processing logic here
        df = pd.read_excel(filepath)
        total_rows = len(df)
        logging.info(f"Total rows in file: {total_rows}")

        # Validate rows
        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            if not all(pd.notna(row[col]) for col in ['Employee Name', 'Email']):
                raise ValueError(f"Missing required data in row {i+1}")
            
            processed_row = {
                'name': row['Employee Name'],
                'email': row['Email']
            }
            results.append(processed_row)

            # Update progress
            if i % max(1, total_rows // 20) == 0:
                progress = min(95, int((i / total_rows) * 100))
                self.update_state(state='PROGRESS', meta={
                    'progress': progress + 5,
                    'message': f'Processing row {i+1}/{total_rows}'
                })

        # Final cleanup
        os.remove(filepath)
        logging.info("File processed successfully")

        return {
            'status': 'SUCCESS',
            'data': results,
            'message': f'Processed {total_rows} rows'
        }
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        logging.error(f"Task failed: {str(e)}")
        raise