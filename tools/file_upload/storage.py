"""
File storage utilities for secure cloud and local file handling
Supports both AWS S3 and local storage with fallback mechanisms
"""

import os
import boto3
import uuid
from datetime import datetime, timedelta
from flask import current_app
from werkzeug.utils import secure_filename

class FileStorage:
    """Unified file storage interface supporting multiple backends"""
    
    def __init__(self):
        self.use_s3 = self._check_s3_config()
        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('S3_REGION', 'us-east-1')
            )
            self.bucket_name = os.environ.get('S3_BUCKET')
    
    def _check_s3_config(self):
        """Check if S3 configuration is available"""
        required_keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'S3_BUCKET']
        return all(os.environ.get(key) for key in required_keys)
    
    def upload_file(self, file, user_id, file_type='general'):
        """
        Upload file to configured storage backend
        
        Args:
            file: FileStorage object from request.files
            user_id: ID of the user uploading the file
            file_type: Category of file (pdf, image, general)
            
        Returns:
            dict: {'success': bool, 'file_path': str, 'file_url': str, 'error': str}
        """
        if not file or file.filename == '':
            return {'success': False, 'error': 'No file provided'}
        
        # Secure filename and add unique identifier
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Create storage path with user organization
        storage_path = f"uploads/{user_id}/{file_type}/{unique_filename}"
        
        try:
            if self.use_s3:
                return self._upload_to_s3(file, storage_path, original_filename)
            else:
                return self._upload_locally(file, storage_path, original_filename)
                
        except Exception as e:
            current_app.logger.error(f"File upload error: {str(e)}")
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    def _upload_to_s3(self, file, storage_path, original_filename):
        """Upload file to AWS S3"""
        try:
            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                storage_path,
                ExtraArgs={
                    'ContentType': file.content_type or 'application/octet-stream',
                    'ContentDisposition': f'attachment; filename="{original_filename}"'
                }
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{storage_path}"
            
            return {
                'success': True,
                'file_path': storage_path,
                'file_url': file_url,
                'storage_type': 's3'
            }
            
        except Exception as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    def _upload_locally(self, file, storage_path, original_filename):
        """Upload file to local storage"""
        # Ensure upload directory exists
        local_dir = os.path.dirname(storage_path)
        os.makedirs(local_dir, exist_ok=True)
        
        # Save file locally
        file.save(storage_path)
        
        return {
            'success': True,
            'file_path': storage_path,
            'file_url': f'/uploads/{os.path.basename(storage_path)}',
            'storage_type': 'local'
        }
    
    def generate_presigned_url(self, file_path, expiration=3600):
        """Generate secure download URL"""
        if self.use_s3:
            try:
                return self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': file_path},
                    ExpiresIn=expiration
                )
            except Exception as e:
                current_app.logger.error(f"Presigned URL generation failed: {e}")
                return None
        else:
            # For local storage, return direct path
            return f'/uploads/{os.path.basename(file_path)}'
    
    def delete_file(self, file_path):
        """Delete file from storage"""
        try:
            if self.use_s3:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
            else:
                if os.path.exists(file_path):
                    os.remove(file_path)
            return True
        except Exception as e:
            current_app.logger.error(f"File deletion failed: {e}")
            return False

# Global storage instance
storage = FileStorage()

def upload_file(file, user_id, file_type='general'):
    """Convenience function for file uploads"""
    return storage.upload_file(file, user_id, file_type)

def get_download_url(file_path, expiration=3600):
    """Convenience function for generating download URLs"""
    return storage.generate_presigned_url(file_path, expiration)