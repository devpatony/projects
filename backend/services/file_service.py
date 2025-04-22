import os
from typing import Optional

class FileService:
    @staticmethod
    def save_uploaded_file(file, upload_folder: str) -> Optional[str]:
        try:
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)
            return filepath
        except Exception as e:
            print(f"File save failed: {str(e)}")
            return None

    @staticmethod
    def cleanup_file(filepath: str) -> None:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"File cleanup failed: {str(e)}")