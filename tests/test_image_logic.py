import pytest
import io
from PIL import Image
import numpy as np
from routers.predict import validate_image
from models.ml_model import preprocess_image

def test_png_magic_bytes():
    # PNG magic bytes: \x89PNG
    png_data = b"\x89PNG\r\n\x1a\n" + b"some data"
    assert validate_image(png_data) is True

def test_jpg_magic_bytes():
    # JPG magic bytes: \xff\xd8\xff
    jpg_data = b"\xff\xd8\xff\xe0" + b"some data"
    assert validate_image(jpg_data) is True

def test_invalid_magic_bytes():
    assert validate_image(b"GIF89a") is False

def test_preprocess_range():
    # Create a dummy image (Red)
    img = Image.new('RGB', (300, 300), color = (255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    byte_im = buf.getvalue()
    
    processed = preprocess_image(byte_im)
    
    # Should be (1, 224, 224, 3)
    assert processed.shape == (1, 224, 224, 3)
    
    # Range should be [0, 255] since we removed the /255.0 and mean/std subtraction
    assert np.max(processed) <= 255.0
    assert np.min(processed) >= 0.0
    # Specifically for pure red image, max should be 255
    assert np.max(processed) == 255.0
