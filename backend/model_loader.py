import os
import asyncio
from typing import Optional
from loguru import logger

class ModelLoader:
    _instance: Optional["ModelLoader"] = None
    _lock = asyncio.Lock()
    _model = None
    _loaded = False
    _load_error: Optional[str] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def load_model(self, model_path: str) -> bool:
        """Load the EfficientNet model asynchronously with thread safety"""
        async with self._lock:
            if self._loaded:
                return True
            
            try:
                logger.info(f"Loading model from {model_path}")
                
                # Check if model file exists
                if not os.path.exists(model_path):
                    self._load_error = f"Model file not found: {model_path}"
                    logger.error(self._load_error)
                    return False
                
                # Import and load model
                from tensorflow.keras.models import load_model
                
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                self._model = await loop.run_in_executor(
                    None,
                    lambda: load_model(model_path, compile=False)
                )
                
                self._loaded = True
                logger.info("Model loaded successfully")
                return True
                
            except Exception as e:
                self._load_error = str(e)
                logger.error(f"Failed to load model: {e}")
                return False
    
    def get_model(self):
        """Get the loaded model or None"""
        return self._model
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self._loaded
    
    def get_load_error(self) -> Optional[str]:
        """Get the error message if model failed to load"""
        return self._load_error
    
    def reload(self):
        """Reset the loader to allow reloading"""
        self._model = None
        self._loaded = False
        self._load_error = None

model_loader = ModelLoader()