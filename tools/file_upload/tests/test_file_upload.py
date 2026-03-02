"""
Tests for file upload functionality
Following the integration guide recommendations for comprehensive testing
"""

import pytest
import io
import os
from unittest.mock import patch, MagicMock
from flask import url_for

def test_upload_index_route(client, authenticated_user):
    """Test that upload page loads correctly"""
    response = client.get('/tools/file_upload/')
    assert response.status_code == 200
    assert b'Upload PDF File' in response.data

def test_api_upload_no_file(client, authenticated_user):
    """Test upload API with no file"""
    response = client.post('/tools/file_upload/api/upload')
    assert response.status_code == 400
    data = response.get_json()
    assert not data['success']
    assert 'No file provided' in data['error']

def test_api_upload_empty_filename(client, authenticated_user):
    """Test upload API with empty filename"""
    data = {'file': (io.BytesIO(b''), '')}
    response = client.post('/tools/file_upload/api/upload', 
                          data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert not data['success']
    assert 'No file selected' in data['error']

def test_api_upload_invalid_file_type(client, authenticated_user):
    """Test upload API with invalid file type"""
    data = {'file': (io.BytesIO(b'fake content'), 'test.txt')}
    response = client.post('/tools/file_upload/api/upload',
                          data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert not data['success']
    assert 'File type not allowed' in data['error']

@patch('tools.file_upload.storage.upload_file')
def test_api_upload_success(mock_upload, client, authenticated_user):
    """Test successful file upload"""
    # Mock storage response
    mock_upload.return_value = {
        'success': True,
        'file_path': 'uploads/1/pdf/test.pdf',
        'storage_type': 'local'
    }
    
    data = {'file': (io.BytesIO(b'%PDF-1.4'), 'test.pdf')}
    response = client.post('/tools/file_upload/api/upload',
                          data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success']
    assert 'test.pdf' in data['filename']

def test_api_validate_valid_file(client, authenticated_user):
    """Test file validation API with valid file"""
    data = {
        'filename': 'test.pdf',
        'filesize': 1024 * 1024  # 1MB
    }
    response = client.post('/tools/file_upload/api/validate', 
                          json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid']

def test_api_validate_invalid_file_type(client, authenticated_user):
    """Test file validation API with invalid file type"""
    data = {
        'filename': 'test.txt',
        'filesize': 1024
    }
    response = client.post('/tools/file_upload/api/validate',
                          json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert not data['valid']
    assert 'File type not supported' in data['error']

def test_api_validate_file_too_large(client, authenticated_user):
    """Test file validation API with oversized file"""
    data = {
        'filename': 'test.pdf',
        'filesize': 100 * 1024 * 1024  # 100MB
    }
    response = client.post('/tools/file_upload/api/validate',
                          json=data)
    assert response.status_code == 200
    data = response.get_json()
    assert not data['valid']
    assert 'File too large' in data['error']

def test_storage_local_upload(app):
    """Test local storage upload functionality"""
    from tools.file_upload.storage import FileStorage
    
    with app.app_context():
        storage = FileStorage()
        
        # Mock file object
        mock_file = MagicMock()
        mock_file.filename = 'test.pdf'
        mock_file.content_type = 'application/pdf'
        mock_file.save = MagicMock()
        
        result = storage._upload_locally(mock_file, 'test/path.pdf', 'test.pdf')
        
        assert result['success']
        assert result['storage_type'] == 'local'
        assert 'file_path' in result

@patch('boto3.client')
def test_storage_s3_config(mock_boto3, app):
    """Test S3 storage configuration"""
    from tools.file_upload.storage import FileStorage
    
    # Mock environment variables
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'S3_BUCKET': 'test_bucket'
    }):
        storage = FileStorage()
        assert storage.use_s3 is True
        assert storage.bucket_name == 'test_bucket'

def test_route_registration(app):
    """Test that file upload routes are properly registered"""
    from tools.file_upload.routes import file_upload_bp
    
    # Check if blueprint is registered
    assert 'file_upload' in [bp.name for bp in app.blueprints.values()]

# Fixtures for testing
@pytest.fixture
def authenticated_user(client):
    """Create an authenticated user session"""
    # This would integrate with your authentication system
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['_fresh'] = True
    return client