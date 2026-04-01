import pytest
import io
import numpy as np
from PIL import Image

from models.ml_model import preprocess_image, predict, CLASS_NAMES

class TestImagePreprocessing:
    def test_resize_image_to_224(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (500, 500), color="red")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        arr = preprocess_image(img_bytes.getvalue())
        assert arr.shape == (1, 224, 224, 3)
    
    def test_convert_to_rgb(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        arr = preprocess_image(img_bytes.getvalue())
        assert arr.shape == (1, 224, 224, 3)
    
    def test_array_conversion(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="blue")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        arr = preprocess_image(img_bytes.getvalue())
        assert arr.dtype in [np.float32, np.float64]
    
    def test_expand_dims(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="yellow")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        arr = preprocess_image(img_bytes.getvalue())
        assert len(arr.shape) == 4

class TestPrediction:
    def test_predict_returns_dict(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (224, 224), color="white")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        result = predict(img_bytes.getvalue())
        
        assert isinstance(result, dict)
        assert "tumor_detected" in result
        assert "tumor_type" in result
        assert "confidence_score" in result
        assert "tumor_location" in result
        assert "analysis_notes" in result
        assert "all_probabilities" in result
    
    def test_predict_valid_tumor_types(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (224, 224), color="gray")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        result = predict(img_bytes.getvalue())
        
        assert result["tumor_type"] in CLASS_NAMES + ["Inconclusive"]
        assert result["confidence_score"] >= 0
        assert result["confidence_score"] <= 100
    
    def test_confidence_score_bounds(self):
        for _ in range(10):
            img_bytes = io.BytesIO()
            img = Image.new("RGB", (224, 224), color="black")
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            
            result = predict(img_bytes.getvalue())
            
            assert 0 <= result["confidence_score"] <= 100
    
    def test_all_probabilities_sum_approx_100(self):
        img_bytes = io.BytesIO()
        img = Image.new("RGB", (224, 224), color="red")
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        
        result = predict(img_bytes.getvalue())
        probs = result["all_probabilities"]
        
        total = sum(probs.values())
        assert 99 <= total <= 101
