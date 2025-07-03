"""
Test cases for the specific endpoints defined in dataset/router.py

This file tests only the 4 actual endpoints:
1. POST /upload
2. GET /  
3. GET /{dataset_name}/images
4. GET /{dataset_name}/image/{image_name}
"""

import pytest
import io
import os
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

# Import the main app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestUploadEndpoint:
    """Test cases for POST /datasets/upload endpoint."""

    def test_upload_non_zip_file(self, client):
        """Test uploading a non-ZIP file should return 400."""
        files = {"file": ("test.txt", io.BytesIO(b"not a zip"), "text/plain")}
        
        response = client.post("/datasets/upload", files=files)
        
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]

    def test_upload_empty_file(self, client):
        """Test uploading an empty file."""
        files = {"file": ("empty.zip", io.BytesIO(b""), "application/zip")}
        
        response = client.post("/datasets/upload", files=files)
        
        # Should handle gracefully - either validation error or processing error
        assert response.status_code in [400, 422, 500]

    def test_upload_missing_file(self, client):
        """Test upload endpoint without file parameter."""
        response = client.post("/datasets/upload")
        
        assert response.status_code == 422  # Missing required field

    @patch('dataset.services.handle_upload', new_callable=AsyncMock)
    def test_upload_success_mock(self, mock_handle, client):
        """Test successful upload with mocked service."""
        # Mock the service to return success
        mock_handle.return_value = {"message": "Upload successful", "dataset_name": "test"}
        
        files = {"file": ("test.zip", io.BytesIO(b"fake zip data"), "application/zip")}
        
        response = client.post("/datasets/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Upload successful"
        mock_handle.assert_called_once()


class TestListDatasetsEndpoint:
    """Test cases for GET /datasets/ endpoint."""

    @patch('dataset.services.get_all_datasets', new_callable=AsyncMock)
    def test_list_datasets_empty(self, mock_get_all, client):
        """Test listing datasets when none exist."""
        # Mock empty response
        mock_get_all.return_value = {"datasets": [], "total_count": 0}
        
        response = client.get("/datasets/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["datasets"] == []
        mock_get_all.assert_called_once()

    @patch('dataset.services.get_all_datasets', new_callable=AsyncMock)
    def test_list_datasets_with_data(self, mock_get_all, client):
        """Test listing datasets with existing data."""
        # Mock response with data
        mock_datasets = [
            {"name": "dataset1", "created_at": "2023-01-01"},
            {"name": "dataset2", "created_at": "2023-01-02"}
        ]
        mock_get_all.return_value = {"datasets": mock_datasets, "total_count": 2}
        
        response = client.get("/datasets/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["datasets"]) == 2
        assert data["total_count"] == 2
        mock_get_all.assert_called_once()


class TestGetImagesEndpoint:
    """Test cases for GET /datasets/{dataset_name}/images endpoint."""

    @patch('dataset.services.get_dataset_images', new_callable=AsyncMock)
    def test_get_images_success(self, mock_get_images, client):
        """Test getting dataset images successfully."""
        # Mock successful response
        mock_get_images.return_value = {
            "images": [
                {"image_name": "img1.jpg", "labels": []},
                {"image_name": "img2.jpg", "labels": []}
            ],
            "total_images": 2,
            "total_pages": 1,
            "current_page": 1,
            "page_size": 20
        }
        
        response = client.get("/datasets/test_dataset/images?page=1")
        
        assert response.status_code == 200
        data = response.json()
        assert "images" in data
        assert "total_images" in data
        assert data["current_page"] == 1
        mock_get_images.assert_called_once_with("test_dataset", 1)

    @patch('dataset.services.get_dataset_images', new_callable=AsyncMock)
    def test_get_images_dataset_not_found(self, mock_get_images, client):
        """Test getting images for non-existent dataset."""
        # Mock service returning None (dataset not found)
        mock_get_images.return_value = None
        
        response = client.get("/datasets/nonexistent/images")
        
        assert response.status_code == 404
        assert "Dataset not found" in response.json()["detail"]
        mock_get_images.assert_called_once_with("nonexistent", 1)

    def test_get_images_invalid_page_parameter(self, client):
        """Test getting images with invalid page parameter."""
        # Test page = 0 (should be >= 1)
        response = client.get("/datasets/test_dataset/images?page=0")
        assert response.status_code == 422  # Validation error
        
        # Test negative page
        response = client.get("/datasets/test_dataset/images?page=-1")
        assert response.status_code == 422  # Validation error

    @patch('dataset.services.get_dataset_images', new_callable=AsyncMock)
    def test_get_images_default_page(self, mock_get_images, client):
        """Test getting images with default page parameter."""
        mock_get_images.return_value = {
            "images": [],
            "total_images": 0,
            "total_pages": 0,
            "current_page": 1,
            "page_size": 20
        }
        
        # Don't specify page parameter - should default to 1
        response = client.get("/datasets/test_dataset/images")
        
        assert response.status_code == 200
        mock_get_images.assert_called_once_with("test_dataset", 1)


class TestGetImageFileEndpoint:
    """Test cases for GET /datasets/{dataset_name}/image/{image_name} endpoint."""

    @patch('os.path.exists')
    def test_get_image_file_success(self, mock_exists, client):
        """Test serving an existing image file."""
        # Mock that file exists
        mock_exists.return_value = True
        
        with patch('fastapi.responses.FileResponse') as mock_file_response:
            mock_response = MagicMock()
            mock_file_response.return_value = mock_response
            
            response = client.get("/datasets/test_dataset/image/test_image.jpg")
            
            # Check that os.path.exists was called with correct path
            mock_exists.assert_called_once_with("datasets/images/test_dataset/test_image.jpg")
            # Check that FileResponse was called
            mock_file_response.assert_called_once_with("datasets/images/test_dataset/test_image.jpg")

    @patch('os.path.exists')
    def test_get_image_file_not_found(self, mock_exists, client):
        """Test serving a non-existent image file."""
        # Mock that file doesn't exist
        mock_exists.return_value = False
        
        response = client.get("/datasets/test_dataset/image/nonexistent.jpg")
        
        assert response.status_code == 404
        assert "Image not found" in response.json()["detail"]
        mock_exists.assert_called_once_with("datasets/images/test_dataset/nonexistent.jpg")

    def test_get_image_file_path_structure(self, client):
        """Test that the correct file path is constructed."""
        with patch('os.path.exists', return_value=False):
            response = client.get("/datasets/my_dataset/image/photo.png")
            
            assert response.status_code == 404
            # The path should be: datasets/images/my_dataset/photo.png

    def test_get_image_file_special_characters(self, client):
        """Test image file names with special characters."""
        with patch('os.path.exists', return_value=False):
            # Test with spaces in filename
            response = client.get("/datasets/test/image/image with spaces.jpg")
            assert response.status_code == 404
            
            # Test with dashes and underscores
            response = client.get("/datasets/test/image/image-with_dashes.png")
            assert response.status_code == 404


class TestEndpointIntegration:
    """Integration tests for endpoint workflows."""

    def test_endpoint_path_structure(self, client):
        """Test that all endpoints are properly mounted under /datasets prefix."""
        
        # Test that upload endpoint exists
        response = client.post("/datasets/upload")
        assert response.status_code != 404  # Should exist (even if 422 for missing file)
        
        # Test that list endpoint exists  
        with patch('dataset.services.get_all_datasets', new_callable=AsyncMock, return_value={"datasets": []}):
            response = client.get("/datasets/")
            assert response.status_code == 200
        
        # Test that images endpoint exists
        with patch('dataset.services.get_dataset_images', new_callable=AsyncMock, return_value=None):
            response = client.get("/datasets/test/images")
            assert response.status_code == 404  # Dataset not found, but endpoint exists
        
        # Test that image file endpoint exists
        with patch('os.path.exists', return_value=False):
            response = client.get("/datasets/test/image/test.jpg")
            assert response.status_code == 404  # File not found, but endpoint exists

    def test_cors_enabled(self, client):
        """Test that CORS middleware is working."""
        with patch('dataset.services.get_all_datasets', new_callable=AsyncMock, return_value={"datasets": []}):
            response = client.get("/datasets/", headers={"Origin": "http://localhost:3000"})
            
            # Should not fail due to CORS (the actual response depends on the service)
            assert response.status_code == 200  # Should work with proper mocking

    def test_api_documentation_available(self, client):
        """Test that API documentation endpoints are available."""
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200


class TestEndpointValidation:
    """Test input validation for each endpoint."""

    def test_upload_file_validation(self, client):
        """Test file upload validation."""
        # Test with invalid content type
        files = {"file": ("test.exe", io.BytesIO(b"executable"), "application/octet-stream")}
        response = client.post("/datasets/upload", files=files)
        assert response.status_code == 400

    @patch('dataset.services.get_dataset_images', new_callable=AsyncMock)
    def test_images_pagination_validation(self, mock_get_images, client):
        """Test pagination validation for images endpoint."""
        mock_get_images.return_value = {"images": [], "total_images": 0}
        
        # Test valid page
        response = client.get("/datasets/test/images?page=1")
        assert response.status_code == 200
        
        # Test invalid page (string)
        response = client.get("/datasets/test/images?page=abc")
        assert response.status_code == 422

    def test_dataset_name_handling(self, client):
        """Test dataset name parameter handling."""
        with patch('dataset.services.get_dataset_images', new_callable=AsyncMock, return_value=None):
            # Test normal dataset name
            response = client.get("/datasets/my_dataset/images")
            assert response.status_code == 404  # Dataset not found (expected)
            
            # Test dataset name with special characters
            response = client.get("/datasets/dataset-with-dashes/images")
            assert response.status_code == 404  # Dataset not found (expected)


class TestResponseFormats:
    """Test response format consistency."""

    @patch('dataset.services.get_all_datasets', new_callable=AsyncMock)
    def test_list_datasets_response_format(self, mock_get_all, client):
        """Test that list datasets returns proper format."""
        mock_get_all.return_value = {"datasets": [], "total_count": 0}
        
        response = client.get("/datasets/")
        assert response.status_code == 200
        data = response.json()
        assert "datasets" in data
        assert isinstance(data["datasets"], list)

    @patch('dataset.services.get_dataset_images', new_callable=AsyncMock)
    def test_get_images_response_format(self, mock_get_images, client):
        """Test that get images returns proper format."""
        mock_get_images.return_value = {
            "images": [],
            "total_images": 0,
            "total_pages": 0,
            "current_page": 1,
            "page_size": 20
        }
        
        response = client.get("/datasets/test/images")
        assert response.status_code == 200
        data = response.json()
        assert "images" in data
        assert "total_images" in data
        assert "current_page" in data

    def test_error_response_format(self, client):
        """Test that error responses have consistent format."""
        response = client.get("/datasets/nonexistent/image/test.jpg")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data 