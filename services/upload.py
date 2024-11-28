import boto3
import os
from datetime import datetime
from typing import Dict, Union, List

R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_DOMAINS = os.getenv("R2_DOMAINS")


class UploadService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=R2_ENDPOINT_URL,
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        )

    def upload_file(self, file, filename):
        try:
            self.s3_client.upload_fileobj(file, R2_BUCKET_NAME, filename)
            file_url = f"{R2_DOMAINS}/{filename}"
            return file_url
        except Exception as e:
            print(f"Failed to upload file : {e}")
            return False


class UploadFiles:
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "mp4"}  # Extension limit
    MAX_FILE_SIZE = 10 * 1024 * 1024  # File size limit

    def allowed_file(self, filename: str) -> bool:
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )

    def process_single_file(self, file) -> Dict[str, Union[str, List[str]]]:
        """Process a single file and return result with any errors"""
        if file.filename == "":
            return {"error": "Empty filename"}

        if not self.allowed_file(file.filename):
            return {"error": "File type not allowed"}

        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)

        if file_length > self.MAX_FILE_SIZE:
            return {"error": "File size exceeds limit"}

        filename = file.filename
        ext_name = os.path.splitext(filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"MEDIA-{timestamp}{ext_name}"

        upload_service = UploadService()

        try:
            file_url = upload_service.upload_file(file, new_filename)
            return {"success": True, "file_url": file_url}
        except Exception as e:
            return {"error": str(e)}
