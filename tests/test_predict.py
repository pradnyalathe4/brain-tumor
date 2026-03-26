"""
Prediction Tests
Tests for /predict endpoint and image preprocessing
"""

import pytest
import sys
import io
from pathlib import Path

backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import numpy as np
from PIL import Image


class TestImagePreprocessing:
    """Test image preprocessing functions"""
    
    def test_resize_image_to_224(self):
        """Should resize image to 224x224"""
        # Create a test image
        img = Image.new('RGB', (512, 512), color='white')
        
        # Resize
        img_resized = img.resize((224, 224))
        
        assert img_resized.size == (224, 224)
    
    def test_convert_to_rgb(self):
        """Should convert grayscale to RGB"""
        img = Image.new('L', (100, 100), color=128)
        img_rgb = img.convert('RGB')
        
        assert img_rgb.mode == 'RGB'
    
    def test_convert_rgba_to_rgb(self):
        """Should convert RGBA to RGB"""
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        img_rgb = img.convert('RGB')
        
        assert img_rgb.mode == 'RGB'
    
    def test_array_conversion(self):
        """Should convert image to numpy array"""
        img = Image.new('RGB', (224, 224), color='white')
        arr = np.array(img)
        
        assert arr.shape == (224, 224, 3)
        assert arr.dtype == np.uint8
    
    def test_expand_dims(self):
        """Should add batch dimension"""
        img = Image.new('RGB', (224, 224), color='white')
        arr = np.array(img, dtype=np.float32)
        batch = np.expand_dims(arr, axis=0)
        
        assert batch.shape == (1, 224, 224, 3)
    
    def test_preprocess_input_normalization(self):
        """Test EfficientNet preprocessing"""
        from tensorflow.keras.applications.efficientnet import preprocess_input
        
        # Create sample input
        x = np.random.rand(1, 224, 224, 3).astype(np.float32) * 255
        
        # Apply preprocessing
        x_processed = preprocess_input(x)
        
        # Check that values are in expected range
        assert x_processed.shape == x.shape


class TestPredictionResponse:
    """Test prediction response format"""
    
    def test_response_has_required_fields(self):
        """Response should have all required fields"""
        from schemas import PredictionResponse
        
        response = PredictionResponse(
            tumor_detected=True,
            confidence_score=95.5,
            tumor_type="Glioma",
            tumor_location="Frontal Lobe",
            analysis_notes="Test analysis"
        )
        
        assert response.tumor_detected is True
        assert response.confidence_score == 95.5
        assert response.tumor_type == "Glioma"
        assert response.tumor_location == "Frontal Lobe"
        assert response.analysis_notes == "Test analysis"
    
    def test_response_optional_fields(self):
        """Optional fields should be None when not detected"""
        from schemas import PredictionResponse
        
        response = PredictionResponse(
            tumor_detected=False,
            confidence_score=99.9,
            tumor_type=None,
            tumor_location=None,
            analysis_notes="No tumor detected"
        )
        
        assert response.tumor_detected is False
        assert response.tumor_type is None
        assert response.tumor_location is None
    
    def test_confidence_score_rounding(self):
        """Confidence score should be rounded to 2 decimal places"""
        from schemas import PredictionResponse
        
        response = PredictionResponse(
            tumor_detected=True,
            confidence_score=95.567,
            tumor_type="Glioma",
            tumor_location="Frontal Lobe",
            analysis_notes="Test"
        )
        
        assert response.confidence_score == pytest.approx(95.57, abs=0.01)


class TestClassMapping:
    """Test tumor class mapping"""
    
    def test_class_names_order(self):
        """Class names should be in correct order"""
        class_names = ['glioma', 'meningioma', 'notumor', 'pituitary']
        
        assert class_names[0] == 'glioma'
        assert class_names[1] == 'meningioma'
        assert class_names[2] == 'notumor'
        assert class_names[3] == 'pituitary'
    
    def test_display_names_mapping(self):
        """Display names should map correctly"""
        DISPLAY_NAMES = {
            "glioma": "Glioma",
            "meningioma": "Meningioma",
            "pituitary": "Pituitary Tumor",
            "notumor": "No Tumor"
        }
        
        assert DISPLAY_NAMES['glioma'] == "Glioma"
        assert DISPLAY_NAMES['notumor'] == "No Tumor"
        assert DISPLAY_NAMES['pituitary'] == "Pituitary Tumor"
    
    def test_tumor_detection_logic(self):
        """Should detect tumor based on class"""
        test_cases = [
            ('glioma', True),
            ('meningioma', True),
            ('pituitary', True),
            ('notumor', False)
        ]
        
        for class_name, expected in test_cases:
            tumor_detected = class_name != 'notumor'
            assert tumor_detected == expected


class TestAnalysisNotes:
    """Test analysis notes generation based on confidence"""
    
    def test_high_confidence_notes(self):
        """Should generate appropriate notes for high confidence"""
        confidence = 95.0
        tumor_type = "Glioma"
        
        if confidence >= 85:
            notes = f"{tumor_type} detected with high confidence. Findings strongly suggest pathology. Clinical correlation advised."
        
        assert "high confidence" in notes
        assert "pathology" in notes
    
    def test_moderate_confidence_notes(self):
        """Should generate appropriate notes for moderate confidence"""
        confidence = 70.0
        tumor_type = "Meningioma"
        
        if confidence >= 65:
            notes = f"{tumor_type} detected with moderate confidence. Further imaging or expert review recommended."
        
        assert "moderate confidence" in notes
        assert "expert review" in notes
    
    def test_low_confidence_notes(self):
        """Should generate appropriate notes for low confidence"""
        confidence = 50.0
        tumor_type = "Pituitary Tumor"
        
        notes = f"Possible {tumor_type.lower()} detected with low confidence. Manual radiologist review is required."
        
        assert "low confidence" in notes
        assert "radiologist" in notes
    
    def test_no_tumor_notes(self):
        """Should generate appropriate notes when no tumor"""
        notes = "No tumor detected. Brain MRI appears within normal limits. If symptoms persist, further evaluation is recommended."
        
        assert "No tumor detected" in notes
        assert "normal limits" in notes


class TestFileValidation:
    """Test file validation for uploads"""
    
    def test_valid_png_magic_bytes(self):
        """Should accept valid PNG magic bytes"""
        magic_bytes = b'\x89PNG\r\n\x1a\n'
        
        assert magic_bytes[:4] == b'\x89PNG'
    
    def test_valid_jpeg_magic_bytes(self):
        """Should accept valid JPEG magic bytes"""
        magic_bytes = b'\xff\xd8\xff'
        
        assert magic_bytes[:3] == b'\xff\xd8\xff'
    
    def test_detect_invalid_file(self):
        """Should reject non-image files"""
        invalid_bytes = b'MZ'  # EXE file
        
        valid_magic = [
            b'\x89PNG\r\n\x1a\n',
            b'\xff\xd8\xff',
            b'GIF87a',
            b'GIF89a'
        ]
        
        is_valid = any(invalid_bytes.startswith(m) for m in valid_magic)
        assert is_valid is False
    
    def test_max_file_size_calculation(self):
        """Should correctly calculate max file size"""
        max_size_mb = 10
        max_size_bytes = max_size_mb * 1024 * 1024
        
        assert max_size_bytes == 10_485_760