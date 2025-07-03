import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Import the YOLO utilities to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.yolo import validate_yolo_structure, parse_labels


class TestValidateYoloStructure:
    """Test cases for YOLO structure validation."""

    def test_valid_structure_all_groups(self, temp_directory):
        """Test validation with all three groups (train, valid, test)."""
        
        # Create valid YOLO structure
        for group in ["train", "valid", "test"]:
            images_dir = Path(temp_directory) / group / "images"
            labels_dir = Path(temp_directory) / group / "labels"
            images_dir.mkdir(parents=True)
            labels_dir.mkdir(parents=True)
        
        # Should not raise any exception
        try:
            validate_yolo_structure(temp_directory)
        except Exception as e:
            pytest.fail(f"Valid structure should not raise exception: {e}")

    def test_valid_structure_train_only(self, temp_directory):
        """Test validation with only train group."""
        
        images_dir = Path(temp_directory) / "train" / "images"
        labels_dir = Path(temp_directory) / "train" / "labels"
        images_dir.mkdir(parents=True)
        labels_dir.mkdir(parents=True)
        
        # Should not raise any exception
        try:
            validate_yolo_structure(temp_directory)
        except Exception as e:
            pytest.fail(f"Valid structure should not raise exception: {e}")

    def test_valid_structure_valid_only(self, temp_directory):
        """Test validation with only valid group."""
        
        images_dir = Path(temp_directory) / "valid" / "images"
        labels_dir = Path(temp_directory) / "valid" / "labels"
        images_dir.mkdir(parents=True)
        labels_dir.mkdir(parents=True)
        
        # Should not raise any exception
        try:
            validate_yolo_structure(temp_directory)
        except Exception as e:
            pytest.fail(f"Valid structure should not raise exception: {e}")

    def test_valid_structure_test_only(self, temp_directory):
        """Test validation with only test group."""
        
        images_dir = Path(temp_directory) / "test" / "images"
        labels_dir = Path(temp_directory) / "test" / "labels"
        images_dir.mkdir(parents=True)
        labels_dir.mkdir(parents=True)
        
        # Should not raise any exception
        try:
            validate_yolo_structure(temp_directory)
        except Exception as e:
            pytest.fail(f"Valid structure should not raise exception: {e}")

    def test_invalid_structure_missing_labels(self, temp_directory):
        """Test validation fails when labels directory is missing."""
        
        # Create only images directory
        images_dir = Path(temp_directory) / "train" / "images"
        images_dir.mkdir(parents=True)
        
        with pytest.raises(ValueError) as exc_info:
            validate_yolo_structure(temp_directory)
        
        assert "At least one of the following directory groups must exist" in str(exc_info.value)

    def test_invalid_structure_missing_images(self, temp_directory):
        """Test validation fails when images directory is missing."""
        
        # Create only labels directory
        labels_dir = Path(temp_directory) / "train" / "labels"
        labels_dir.mkdir(parents=True)
        
        with pytest.raises(ValueError) as exc_info:
            validate_yolo_structure(temp_directory)
        
        assert "At least one of the following directory groups must exist" in str(exc_info.value)

    def test_invalid_structure_no_directories(self, temp_directory):
        """Test validation fails when no required directories exist."""
        
        with pytest.raises(ValueError) as exc_info:
            validate_yolo_structure(temp_directory)
        
        assert "At least one of the following directory groups must exist" in str(exc_info.value)

    def test_invalid_structure_incomplete_groups(self, temp_directory):
        """Test validation fails when groups are incomplete."""
        
        # Create train/images but no train/labels
        images_dir = Path(temp_directory) / "train" / "images"
        images_dir.mkdir(parents=True)
        
        # Create valid/labels but no valid/images  
        labels_dir = Path(temp_directory) / "valid" / "labels"
        labels_dir.mkdir(parents=True)
        
        with pytest.raises(ValueError) as exc_info:
            validate_yolo_structure(temp_directory)
        
        assert "At least one of the following directory groups must exist" in str(exc_info.value)


class TestParseLabels:
    """Test cases for YOLO label parsing."""

    def test_parse_labels_success(self, temp_directory):
        """Test successful parsing of YOLO labels."""
        
        dataset_name = "test_dataset"
        
        # Create train structure
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        # Create test image and label files
        (train_images_dir / "image1.jpg").write_bytes(b"fake image data")
        (train_images_dir / "image2.png").write_bytes(b"fake image data")
        (train_labels_dir / "image1.txt").write_text("0 0.5 0.5 0.2 0.3\n1 0.3 0.7 0.1 0.2")
        (train_labels_dir / "image2.txt").write_text("2 0.4 0.6 0.15 0.25")
        
        with patch('os.makedirs'), patch('shutil.copy'):
            images, labels = parse_labels(temp_directory, dataset_name)
        
        # Check results
        assert len(images) == 2
        assert "image1.jpg" in labels
        assert "image2.png" in labels
        
        # Check label parsing
        assert len(labels["image1.jpg"]) == 2
        assert labels["image1.jpg"][0]["class"] == "0"
        assert labels["image1.jpg"][0]["bbox"] == ["0.5", "0.5", "0.2", "0.3"]
        assert labels["image1.jpg"][1]["class"] == "1"
        assert labels["image1.jpg"][1]["bbox"] == ["0.3", "0.7", "0.1", "0.2"]
        
        assert len(labels["image2.png"]) == 1
        assert labels["image2.png"][0]["class"] == "2"
        assert labels["image2.png"][0]["bbox"] == ["0.4", "0.6", "0.15", "0.25"]

    def test_parse_labels_multiple_groups(self, temp_directory):
        """Test parsing labels from multiple groups (train, valid, test)."""
        
        dataset_name = "multi_group_dataset"
        
        for group in ["train", "valid", "test"]:
            images_dir = Path(temp_directory) / group / "images"
            labels_dir = Path(temp_directory) / group / "labels"
            images_dir.mkdir(parents=True)
            labels_dir.mkdir(parents=True)
            
            # Create test files for each group
            (images_dir / f"{group}_image.jpg").write_bytes(b"fake image data")
            (labels_dir / f"{group}_image.txt").write_text(f"{group[0]} 0.5 0.5 0.2 0.3")
        
        with patch('os.makedirs'), patch('shutil.copy'):
            images, labels = parse_labels(temp_directory, dataset_name)
        
        # Should have images from all groups
        assert len(images) == 3
        assert "train_image.jpg" in labels
        assert "valid_image.jpg" in labels
        assert "test_image.jpg" in labels

    def test_parse_labels_missing_label_file(self, temp_directory):
        """Test parsing when label file is missing for an image."""
        
        dataset_name = "missing_labels_dataset"
        
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        # Create image without corresponding label
        (train_images_dir / "image_no_label.jpg").write_bytes(b"fake image data")
        
        with patch('os.makedirs'), patch('shutil.copy'):
            images, labels = parse_labels(temp_directory, dataset_name)
        
        # Should still include the image but with empty labels
        assert len(images) == 1
        assert "image_no_label.jpg" in labels
        assert labels["image_no_label.jpg"] == []

    def test_parse_labels_invalid_label_format(self, temp_directory):
        """Test parsing with invalid label format."""
        
        dataset_name = "invalid_labels_dataset"
        
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        # Create image and label with invalid format
        (train_images_dir / "image1.jpg").write_bytes(b"fake image data")
        (train_labels_dir / "image1.txt").write_text("invalid format\n0 0.5 0.5")  # Invalid lines
        
        with patch('os.makedirs'), patch('shutil.copy'):
            images, labels = parse_labels(temp_directory, dataset_name)
        
        # Should skip invalid lines and process valid ones
        assert len(images) == 1
        assert "image1.jpg" in labels
        # Only the invalid lines should be skipped, valid lines (if any) should be included
        assert len(labels["image1.jpg"]) == 0  # Both lines are invalid in this case

    def test_parse_labels_supported_image_extensions(self, temp_directory):
        """Test that only supported image extensions are processed."""
        
        dataset_name = "extensions_dataset"
        
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        # Create files with different extensions
        (train_images_dir / "image1.jpg").write_bytes(b"fake image data")
        (train_images_dir / "image2.jpeg").write_bytes(b"fake image data")
        (train_images_dir / "image3.png").write_bytes(b"fake image data")
        (train_images_dir / "image4.txt").write_bytes(b"not an image")  # Should be ignored
        (train_images_dir / "image5.gif").write_bytes(b"unsupported format")  # Should be ignored
        
        with patch('os.makedirs'), patch('shutil.copy'):
            images, labels = parse_labels(temp_directory, dataset_name)
        
        # Should only process jpg, jpeg, png
        assert len(images) == 3
        image_names = [os.path.basename(img) for img in images]
        assert "image1.jpg" in image_names
        assert "image2.jpeg" in image_names
        assert "image3.png" in image_names
        assert "image4.txt" not in image_names
        assert "image5.gif" not in image_names

    def test_parse_labels_creates_output_directory(self, temp_directory):
        """Test that output directory is created."""
        
        dataset_name = "output_dir_test"
        
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        (train_images_dir / "image1.jpg").write_bytes(b"fake image data")
        
        with patch('os.makedirs') as mock_makedirs, patch('shutil.copy'):
            parse_labels(temp_directory, dataset_name)
        
        # Should create the output directory
        mock_makedirs.assert_called_with(
            os.path.join("datasets", "images", dataset_name), 
            exist_ok=True
        )

    def test_parse_labels_copies_images(self, temp_directory):
        """Test that images are copied to output directory."""
        
        dataset_name = "copy_test"
        
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        image_path = train_images_dir / "image1.jpg"
        image_path.write_bytes(b"fake image data")
        
        with patch('os.makedirs'), \
             patch('shutil.copy') as mock_copy, \
             patch('os.path.exists', return_value=False):
            
            parse_labels(temp_directory, dataset_name)
        
        # Should copy the image
        mock_copy.assert_called_once()
        call_args = mock_copy.call_args[0]
        assert str(image_path) == call_args[0]
        assert call_args[1].endswith("image1.jpg")

    def test_parse_labels_skips_existing_images(self, temp_directory):
        """Test that existing images in output directory are not copied again."""
        
        dataset_name = "skip_existing_test"
        
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        train_images_dir.mkdir(parents=True)
        train_labels_dir.mkdir(parents=True)
        
        (train_images_dir / "image1.jpg").write_bytes(b"fake image data")
        (train_labels_dir / "image1.txt").write_text("0 0.5 0.5 0.2 0.3")  # Create corresponding label file
        
        with patch('os.makedirs'), \
             patch('shutil.copy') as mock_copy, \
             patch('os.path.exists', return_value=True):  # Simulate existing file
            
            parse_labels(temp_directory, dataset_name)
        
        # Should not copy if file already exists
        mock_copy.assert_not_called()


class TestYoloIntegration:
    """Integration tests for YOLO processing workflow."""

    def test_complete_yolo_processing_workflow(self, temp_directory):
        """Test complete workflow from validation to parsing."""
        
        dataset_name = "complete_workflow_test"
        
        # Create valid YOLO structure
        train_images_dir = Path(temp_directory) / "train" / "images"
        train_labels_dir = Path(temp_directory) / "train" / "labels"
        valid_images_dir = Path(temp_directory) / "valid" / "images"
        valid_labels_dir = Path(temp_directory) / "valid" / "labels"
        
        for dir_path in [train_images_dir, train_labels_dir, valid_images_dir, valid_labels_dir]:
            dir_path.mkdir(parents=True)
        
        # Create test data
        (train_images_dir / "train1.jpg").write_bytes(b"fake image data")
        (train_labels_dir / "train1.txt").write_text("0 0.5 0.5 0.2 0.3")
        (valid_images_dir / "valid1.jpg").write_bytes(b"fake image data")
        (valid_labels_dir / "valid1.txt").write_text("1 0.3 0.7 0.1 0.2")
        
        # Step 1: Validate structure
        try:
            validate_yolo_structure(temp_directory)
        except Exception as e:
            pytest.fail(f"Validation should succeed: {e}")
        
        # Step 2: Parse labels
        with patch('os.makedirs'), patch('shutil.copy'):
            images, labels = parse_labels(temp_directory, dataset_name)
        
        # Verify results
        assert len(images) == 2
        assert len(labels) == 2
        assert "train1.jpg" in labels
        assert "valid1.jpg" in labels
        
        # Verify label content
        assert labels["train1.jpg"][0]["class"] == "0"
        assert labels["valid1.jpg"][0]["class"] == "1" 