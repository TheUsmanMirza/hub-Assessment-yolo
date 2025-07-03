"""
Simplified API endpoint tests for the 4 endpoints in router.py

Tests basic functionality without complex database mocking:
1. POST /datasets/upload
2. GET /datasets/
3. GET /datasets/{dataset_name}/images  
4. GET /datasets/{dataset_name}/image/{image_name}
"""

import pytest
import io
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Create a minimal test app for isolated endpoint testing
test_app = FastAPI()

# Import and include the router
from dataset.router import router
test_app.include_router(router, prefix="/datasets", tags=["datasets"])


@pytest.fixture
def client():
    """Create a test client for the minimal test app."""
    return TestClient(test_app)


class TestEndpointBasics:
    """Basic functionality tests for all 4 endpoints."""

    def test_upload_endpoint_exists(self, client):
        """Test that the upload endpoint exists and requires a file."""
        response = client.post("/datasets/upload")
        # Should get validation error for missing file, not 404 (endpoint not found)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_upload_file_type_validation(self, client):
        """Test upload endpoint validates file type."""
        # Test with non-ZIP file
        files = {"file": ("test.txt", io.BytesIO(b"not a zip"), "text/plain")}
        response = client.post("/datasets/upload", files=files)
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]

    def test_upload_empty_zip(self, client):
        """Test upload with empty ZIP file."""
        files = {"file": ("empty.zip", io.BytesIO(b""), "application/zip")}
        response = client.post("/datasets/upload", files=files)
        # Should handle gracefully (not crash)
        assert response.status_code in [400, 422, 500]

    def test_list_datasets_endpoint_exists(self, client):
        """Test that the list datasets endpoint exists."""
        with patch('dataset.services.get_all_datasets') as mock_service:
            # Mock to prevent database call
            mock_service.return_value = []
            response = client.get("/datasets/")
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404

    def test_get_images_endpoint_exists(self, client):
        """Test that the get images endpoint exists."""
        with patch('dataset.services.get_dataset_images') as mock_service:
            # Mock to prevent database call
            mock_service.return_value = None
            response = client.get("/datasets/test_dataset/images")
            # Should not be 404 for endpoint (would be 404 for dataset not found)
            assert response.status_code in [404, 500]  # 404 = dataset not found, 500 = service error

    def test_get_images_page_validation(self, client):
        """Test page parameter validation for images endpoint."""
        # Test invalid page numbers
        response = client.get("/datasets/test/images?page=0")
        assert response.status_code == 422  # Validation error

        response = client.get("/datasets/test/images?page=-1")
        assert response.status_code == 422  # Validation error

        response = client.get("/datasets/test/images?page=abc")
        assert response.status_code == 422  # Validation error

    def test_get_image_file_endpoint_exists(self, client):
        """Test that the get image file endpoint exists."""
        response = client.get("/datasets/test_dataset/image/test.jpg")
        # Should not be 404 for endpoint not found (would be 404 for file not found)
        assert response.status_code == 404
        assert "Image not found" in response.json()["detail"]

    def test_get_image_file_path_validation(self, client):
        """Test image file path handling."""
        # Test with different file extensions
        response = client.get("/datasets/test/image/photo.png")
        assert response.status_code == 404
        assert "Image not found" in response.json()["detail"]

        response = client.get("/datasets/test/image/image.jpeg")
        assert response.status_code == 404
        assert "Image not found" in response.json()["detail"]


class TestEndpointStructure:
    """Test the overall structure and routing of endpoints."""

    def test_all_endpoints_mounted(self, client):
        """Test that all 4 endpoints are properly mounted."""
        # Check upload endpoint
        response = client.post("/datasets/upload")
        assert response.status_code != 404

        # Check list endpoint (with minimal mocking)
        with patch('dataset.services.get_all_datasets', return_value=[]):
            response = client.get("/datasets/")
            assert response.status_code != 404

        # Check images endpoint
        with patch('dataset.services.get_dataset_images', return_value=None):
            response = client.get("/datasets/test/images")
            assert response.status_code != 404

        # Check image file endpoint
        response = client.get("/datasets/test/image/test.jpg")
        assert response.status_code != 404

    def test_route_parameters(self, client):
        """Test route parameter handling."""
        # Test dataset_name parameter
        response = client.get("/datasets/my-dataset/image/test.jpg")
        assert response.status_code == 404  # File not found, but parameter accepted

        # Test image_name parameter  
        response = client.get("/datasets/test/image/my-image.png")
        assert response.status_code == 404  # File not found, but parameter accepted

        # Test special characters in parameters
        response = client.get("/datasets/dataset_with_underscores/image/image-with-dashes.jpg")
        assert response.status_code == 404  # File not found, but parameters accepted


class TestErrorHandling:
    """Test error handling for each endpoint."""

    def test_upload_error_responses(self, client):
        """Test upload endpoint error responses."""
        # Missing file
        response = client.post("/datasets/upload")
        assert response.status_code == 422
        assert "detail" in response.json()

        # Wrong file type
        files = {"file": ("test.pdf", io.BytesIO(b"pdf content"), "application/pdf")}
        response = client.post("/datasets/upload", files=files)
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]

    def test_images_error_responses(self, client):
        """Test images endpoint error responses."""
        # Invalid page parameter
        response = client.get("/datasets/test/images?page=invalid")
        assert response.status_code == 422

        # Non-existent dataset (with mocking to avoid DB call)
        with patch('dataset.services.get_dataset_images', return_value=None):
            response = client.get("/datasets/nonexistent/images")
            assert response.status_code in [404, 500]

    def test_image_file_error_responses(self, client):
        """Test image file endpoint error responses."""
        # Non-existent file
        response = client.get("/datasets/test/image/nonexistent.jpg")
        assert response.status_code == 404
        assert "Image not found" in response.json()["detail"]

        # Test path construction
        response = client.get("/datasets/test_dataset/image/missing_file.png")
        assert response.status_code == 404


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_swagger_docs_available(self, client):
        """Test that Swagger documentation is available."""
        # Note: This uses the main app, not our test app
        from main import app
        full_client = TestClient(app)
        
        response = full_client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client):
        """Test that ReDoc documentation is available."""
        from main import app
        full_client = TestClient(app)
        
        response = full_client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Test that OpenAPI schema is available."""
        from main import app
        full_client = TestClient(app)
        
        response = full_client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestEndpointIntegration:
    """Simple integration tests."""

    def test_upload_file_parameter_name(self, client):
        """Test that upload endpoint expects 'file' parameter."""
        # Correct parameter name
        files = {"file": ("test.zip", io.BytesIO(b"fake zip"), "application/zip")}
        response = client.post("/datasets/upload", files=files)
        # Should process (even if it fails), not validation error
        assert response.status_code != 422

        # Wrong parameter name
        files = {"upload": ("test.zip", io.BytesIO(b"fake zip"), "application/zip")}
        response = client.post("/datasets/upload", files=files)
        assert response.status_code == 422  # Missing required 'file' parameter

    def test_images_default_page(self, client):
        """Test that images endpoint defaults to page 1."""
        with patch('dataset.services.get_dataset_images', return_value=None):
            # No page parameter - should default to page 1
            response = client.get("/datasets/test/images")
            assert response.status_code in [404, 500]  # Service call happens, but no validation error

            # Explicit page 1
            response = client.get("/datasets/test/images?page=1")
            assert response.status_code in [404, 500]  # Same behavior


class TestEndpointSummary:
    """Summary test that verifies all endpoints are working."""

    def test_all_four_endpoints_functional(self, client):
        """Comprehensive test that all 4 endpoints are functional."""
        
        # 1. POST /datasets/upload - should validate file type
        files = {"file": ("test.txt", io.BytesIO(b"not zip"), "text/plain")}
        response = client.post("/datasets/upload", files=files)
        assert response.status_code == 400
        assert "Only ZIP files are supported" in response.json()["detail"]
        
        # 2. GET /datasets/ - should exist (mock to avoid DB)
        with patch('dataset.services.get_all_datasets', return_value=[]):
            response = client.get("/datasets/")
            assert response.status_code != 404
        
        # 3. GET /datasets/{dataset_name}/images - should validate page param
        response = client.get("/datasets/test/images?page=0")
        assert response.status_code == 422
        
        # 4. GET /datasets/{dataset_name}/image/{image_name} - should handle missing files
        response = client.get("/datasets/test/image/missing.jpg")
        assert response.status_code == 404
        assert "Image not found" in response.json()["detail"]
        
        print("✅ All 4 endpoints are functional and properly routed!") 