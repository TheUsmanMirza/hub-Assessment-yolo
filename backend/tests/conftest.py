import pytest
import asyncio
import os
import tempfile
import zipfile
from pathlib import Path


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def create_test_zip():
    """Create a test ZIP file with YOLO structure."""
    def _create_zip(structure_type="valid", filename="test_dataset.zip"):
        # Create a temporary ZIP file
        import io
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if structure_type == "valid":
                # Create valid YOLO structure
                zip_file.writestr("train/images/image1.jpg", b"fake image data")
                zip_file.writestr("train/images/image2.jpg", b"fake image data")
                zip_file.writestr("train/labels/image1.txt", "0 0.5 0.5 0.2 0.3")
                zip_file.writestr("train/labels/image2.txt", "1 0.3 0.7 0.1 0.2")
                zip_file.writestr("valid/images/image3.jpg", b"fake image data")
                zip_file.writestr("valid/labels/image3.txt", "0 0.4 0.6 0.15 0.25")
            
            elif structure_type == "invalid":
                # Create invalid structure (missing labels directory)
                zip_file.writestr("train/images/image1.jpg", b"fake image data")
                zip_file.writestr("train/images/image2.jpg", b"fake image data")
            
            elif structure_type == "empty":
                # Create empty ZIP
                pass
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    return _create_zip


@pytest.fixture
def sample_dataset_data():
    """Sample dataset data for MongoDB."""
    return {
        "_id": "test_dataset_id",
        "name": "test_dataset",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "total_images": 3,
        "images": {
            "image1.jpg": [{"class": "0", "bbox": ["0.5", "0.5", "0.2", "0.3"]}],
            "image2.jpg": [{"class": "1", "bbox": ["0.3", "0.7", "0.1", "0.2"]}],
            "image3.jpg": [{"class": "0", "bbox": ["0.4", "0.6", "0.15", "0.25"]}]
        }
    }


@pytest.fixture
def mock_file_operations():
    """Mock file system operations."""
    with patch('os.makedirs'), \
         patch('os.path.exists', return_value=True), \
         patch('shutil.rmtree'), \
         patch('aiofiles.open'), \
         patch('os.listdir', return_value=[]):
        yield


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    # Create a simple RGB image
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    return img_buffer.getvalue()


@pytest.fixture
def mock_uuid():
    """Mock UUID generation for consistent testing."""
    with patch('uuid.uuid4', return_value=MagicMock(spec=['__str__'])) as mock:
        mock.return_value.__str__.return_value = "test-uuid-123"
        yield mock 