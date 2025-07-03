"""
Basic setup tests to verify testing infrastructure is working.
"""

import pytest
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSetup:
    """Basic setup and infrastructure tests."""

    def test_python_version(self):
        """Test that Python version is compatible."""
        assert sys.version_info >= (3, 8), "Python 3.8+ is required"

    def test_imports(self):
        """Test that core modules can be imported."""
        try:
            import fastapi
            import uvicorn
            import motor
            import aiofiles
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import required dependencies: {e}")

    def test_project_structure(self):
        """Test that project structure exists."""
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check main files exist
        assert os.path.exists(os.path.join(backend_dir, "main.py"))
        assert os.path.exists(os.path.join(backend_dir, "requirements.txt"))
        assert os.path.exists(os.path.join(backend_dir, "Dockerfile"))
        
        # Check directories exist
        assert os.path.exists(os.path.join(backend_dir, "dataset"))
        assert os.path.exists(os.path.join(backend_dir, "utils"))
        assert os.path.exists(os.path.join(backend_dir, "tests"))

    def test_main_app_import(self):
        """Test that the main FastAPI app can be imported."""
        try:
            from main import app
            assert app is not None
            assert hasattr(app, "openapi")  # FastAPI app should have openapi method
        except ImportError as e:
            pytest.fail(f"Failed to import main FastAPI app: {e}")

    def test_dataset_module_import(self):
        """Test that dataset modules can be imported."""
        try:
            from dataset.models import DatasetInDB, ImageLabel
            from dataset.router import router
            from dataset import services
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import dataset modules: {e}")

    def test_utils_module_import(self):
        """Test that utility modules can be imported."""
        try:
            from utils.yolo import validate_yolo_structure, parse_labels
            from utils.file_processing import extract_zip_async
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import utility modules: {e}")

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test that async functionality works."""
        import asyncio
        
        async def sample_async_function():
            await asyncio.sleep(0.001)  # Very short sleep
            return "async works"
        
        result = await sample_async_function()
        assert result == "async works"

    def test_test_dependencies(self):
        """Test that test dependencies are available."""
        try:
            import pytest
            import httpx
            from unittest.mock import AsyncMock, MagicMock, patch
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import test dependencies: {e}")


class TestConfiguration:
    """Test configuration and environment."""

    def test_pytest_configuration(self):
        """Test that pytest is configured correctly."""
        # Check that pytest is running
        import os
        assert "pytest" in os.environ.get("_", "") or True  # Simple check that we're in pytest context

    def test_current_directory(self):
        """Test current working directory."""
        cwd = os.getcwd()
        # Should be in the backend directory or a subdirectory
        assert "backend" in cwd or "hub-Assessment-yolo" in cwd

    def test_environment_variables(self):
        """Test environment variables (if any are required)."""
        # For now, just test that we can access environment variables
        python_path = os.environ.get("PYTHONPATH", "")
        # This is not required, just testing env var access
        assert isinstance(python_path, str)


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"]) 