import pytest
import os
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio

# Import the file processing utilities to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_processing import extract_zip_async


class TestExtractZipAsync:
    """Test cases for async ZIP file extraction."""

    @pytest.mark.asyncio
    async def test_extract_zip_simple_structure(self, temp_directory):
        """Test extraction of ZIP with simple file structure."""
        
        # Create a test ZIP file with multiple top-level items
        zip_path = Path(temp_directory) / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
            zf.writestr("dir1/file3.txt", "content3")
            zf.writestr("dir2/file4.txt", "content4")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return None for multiple top-level directories
        assert result is None
        
        # Verify files were extracted
        assert (dest_path / "file1.txt").exists()
        assert (dest_path / "file2.txt").exists()
        assert (dest_path / "dir1" / "file3.txt").exists()
        assert (dest_path / "dir2" / "file4.txt").exists()

    @pytest.mark.asyncio
    async def test_extract_zip_single_top_directory(self, temp_directory):
        """Test extraction of ZIP with single top-level directory."""
        
        zip_path = Path(temp_directory) / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("dataset/train/images/img1.jpg", "fake image")
            zf.writestr("dataset/train/labels/img1.txt", "0 0.5 0.5 0.2 0.3")
            zf.writestr("dataset/valid/images/img2.jpg", "fake image")
            zf.writestr("dataset/valid/labels/img2.txt", "1 0.3 0.7 0.1 0.2")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return the path to the single top-level directory
        expected_path = str(dest_path / "dataset")
        assert result == expected_path
        
        # Verify files were extracted correctly
        assert (dest_path / "dataset" / "train" / "images" / "img1.jpg").exists()
        assert (dest_path / "dataset" / "train" / "labels" / "img1.txt").exists()

    @pytest.mark.asyncio
    async def test_extract_zip_multiple_top_directories(self, temp_directory):
        """Test extraction of ZIP with multiple top-level directories."""
        
        zip_path = Path(temp_directory) / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("dataset1/file1.txt", "content1")
            zf.writestr("dataset2/file2.txt", "content2")
            zf.writestr("readme.txt", "readme content")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return None for multiple top-level items
        assert result is None
        
        # Verify all items were extracted
        assert (dest_path / "dataset1" / "file1.txt").exists()
        assert (dest_path / "dataset2" / "file2.txt").exists()
        assert (dest_path / "readme.txt").exists()

    @pytest.mark.asyncio
    async def test_extract_zip_empty_archive(self, temp_directory):
        """Test extraction of empty ZIP file."""
        
        zip_path = Path(temp_directory) / "empty.zip"
        
        # Create empty ZIP file
        with zipfile.ZipFile(zip_path, 'w') as zf:
            pass  # Empty ZIP
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return None for empty archive
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_zip_files_only_no_directories(self, temp_directory):
        """Test extraction of ZIP containing only files (no directories)."""
        
        zip_path = Path(temp_directory) / "files_only.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
            zf.writestr("file3.txt", "content3")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return None since there are no directories
        assert result is None
        
        # Verify files were extracted
        assert (dest_path / "file1.txt").exists()
        assert (dest_path / "file2.txt").exists()
        assert (dest_path / "file3.txt").exists()

    @pytest.mark.asyncio
    async def test_extract_zip_nested_single_directory(self, temp_directory):
        """Test extraction with nested structure under single top directory."""
        
        zip_path = Path(temp_directory) / "nested.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("yolo_dataset/train/images/deep/nested/img1.jpg", "fake image")
            zf.writestr("yolo_dataset/train/labels/deep/nested/img1.txt", "0 0.5 0.5 0.2 0.3")
            zf.writestr("yolo_dataset/config.yaml", "config content")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return the path to the single top-level directory
        expected_path = str(dest_path / "yolo_dataset")
        assert result == expected_path
        
        # Verify nested structure was preserved
        assert (dest_path / "yolo_dataset" / "train" / "images" / "deep" / "nested" / "img1.jpg").exists()

    @pytest.mark.asyncio
    async def test_extract_zip_nonexistent_file(self, temp_directory):
        """Test extraction of non-existent ZIP file."""
        
        zip_path = Path(temp_directory) / "nonexistent.zip"
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        with pytest.raises(FileNotFoundError):
            await extract_zip_async(str(zip_path), str(dest_path))

    @pytest.mark.asyncio
    async def test_extract_zip_corrupted_file(self, temp_directory):
        """Test extraction of corrupted ZIP file."""
        
        zip_path = Path(temp_directory) / "corrupted.zip"
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        # Create a file that's not a valid ZIP
        zip_path.write_bytes(b"this is not a zip file")
        
        with pytest.raises(zipfile.BadZipFile):
            await extract_zip_async(str(zip_path), str(dest_path))

    @pytest.mark.asyncio
    async def test_extract_zip_permission_error(self, temp_directory):
        """Test extraction when destination has permission issues."""
        
        zip_path = Path(temp_directory) / "test.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
        
        # Mock permission error during extraction
        with patch('zipfile.ZipFile.extractall', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                await extract_zip_async(str(zip_path), str(temp_directory))

    @pytest.mark.asyncio
    async def test_extract_zip_case_sensitivity(self, temp_directory):
        """Test extraction handles case-sensitive paths correctly."""
        
        zip_path = Path(temp_directory) / "case_test.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("DATASET/Train/Images/img1.jpg", "fake image")
            zf.writestr("DATASET/Train/Labels/img1.txt", "0 0.5 0.5 0.2 0.3")
            zf.writestr("DATASET/Valid/Images/img2.jpg", "fake image")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return the path to the single top-level directory
        expected_path = str(dest_path / "DATASET")
        assert result == expected_path

    @pytest.mark.asyncio
    async def test_extract_zip_special_characters(self, temp_directory):
        """Test extraction with special characters in filenames."""
        
        zip_path = Path(temp_directory) / "special_chars.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("dataset/files/image with spaces.jpg", "fake image")
            zf.writestr("dataset/files/image-with-dashes.jpg", "fake image")
            zf.writestr("dataset/files/image_with_underscores.jpg", "fake image")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should handle special characters correctly
        expected_path = str(dest_path / "dataset")
        assert result == expected_path
        
        # Verify files with special characters were extracted
        assert (dest_path / "dataset" / "files" / "image with spaces.jpg").exists()
        assert (dest_path / "dataset" / "files" / "image-with-dashes.jpg").exists()
        assert (dest_path / "dataset" / "files" / "image_with_underscores.jpg").exists()


class TestFileProcessingIntegration:
    """Integration tests for file processing workflows."""

    @pytest.mark.asyncio
    async def test_yolo_dataset_extraction_workflow(self, temp_directory):
        """Test complete workflow of extracting a YOLO dataset."""
        
        # Create a realistic YOLO dataset ZIP
        zip_path = Path(temp_directory) / "yolo_dataset.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            # Train set
            zf.writestr("yolo_dataset/train/images/img001.jpg", b"fake image data")
            zf.writestr("yolo_dataset/train/images/img002.jpg", b"fake image data")
            zf.writestr("yolo_dataset/train/labels/img001.txt", "0 0.5 0.5 0.2 0.3")
            zf.writestr("yolo_dataset/train/labels/img002.txt", "1 0.3 0.7 0.1 0.2")
            
            # Valid set
            zf.writestr("yolo_dataset/valid/images/img003.jpg", b"fake image data")
            zf.writestr("yolo_dataset/valid/labels/img003.txt", "0 0.4 0.6 0.15 0.25")
            
            # Test set
            zf.writestr("yolo_dataset/test/images/img004.jpg", b"fake image data")
            zf.writestr("yolo_dataset/test/labels/img004.txt", "2 0.7 0.8 0.1 0.1")
            
            # Additional files
            zf.writestr("yolo_dataset/classes.txt", "person\ncar\nbike")
            zf.writestr("yolo_dataset/README.txt", "Dataset information")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        # Extract the ZIP
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return the dataset directory
        expected_path = str(dest_path / "yolo_dataset")
        assert result == expected_path
        
        # Verify YOLO structure was preserved
        dataset_path = dest_path / "yolo_dataset"
        
        # Check train structure
        assert (dataset_path / "train" / "images" / "img001.jpg").exists()
        assert (dataset_path / "train" / "images" / "img002.jpg").exists()
        assert (dataset_path / "train" / "labels" / "img001.txt").exists()
        assert (dataset_path / "train" / "labels" / "img002.txt").exists()
        
        # Check valid structure
        assert (dataset_path / "valid" / "images" / "img003.jpg").exists()
        assert (dataset_path / "valid" / "labels" / "img003.txt").exists()
        
        # Check test structure
        assert (dataset_path / "test" / "images" / "img004.jpg").exists()
        assert (dataset_path / "test" / "labels" / "img004.txt").exists()
        
        # Check additional files
        assert (dataset_path / "classes.txt").exists()
        assert (dataset_path / "README.txt").exists()
        
        # Verify file contents
        assert (dataset_path / "train" / "labels" / "img001.txt").read_text() == "0 0.5 0.5 0.2 0.3"
        assert (dataset_path / "classes.txt").read_text() == "person\ncar\nbike"

    @pytest.mark.asyncio
    async def test_malformed_yolo_zip_extraction(self, temp_directory):
        """Test extraction of malformed YOLO dataset ZIP."""
        
        zip_path = Path(temp_directory) / "malformed.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            # Missing train/labels directory
            zf.writestr("dataset/train/images/img1.jpg", b"fake image")
            # Missing valid/images directory  
            zf.writestr("dataset/valid/labels/img2.txt", "0 0.5 0.5 0.2 0.3")
            # Random files
            zf.writestr("dataset/random_file.txt", "random content")
        
        dest_path = Path(temp_directory) / "extracted"
        dest_path.mkdir()
        
        # Should still extract successfully
        result = await extract_zip_async(str(zip_path), str(dest_path))
        
        # Should return the dataset directory
        expected_path = str(dest_path / "dataset")
        assert result == expected_path
        
        # Verify partial structure was extracted
        assert (dest_path / "dataset" / "train" / "images" / "img1.jpg").exists()
        assert (dest_path / "dataset" / "valid" / "labels" / "img2.txt").exists()
        assert (dest_path / "dataset" / "random_file.txt").exists()
        
        # Missing directories should not exist
        assert not (dest_path / "dataset" / "train" / "labels").exists()
        assert not (dest_path / "dataset" / "valid" / "images").exists() 