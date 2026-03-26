from fastapi import HTTPException, status

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500, code: str = "internal_error"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)

class AuthError(AppException):
    def __init__(self, message: str = "Authentication failed", status_code: int = 401):
        super().__init__(message, status_code, "auth_error")

class ModelLoadError(AppException):
    def __init__(self, message: str = "Model loading failed"):
        super().__init__(message, 503, "model_not_loaded")

class InvalidImageError(AppException):
    def __init__(self, message: str = "Invalid image file"):
        super().__init__(message, 400, "invalid_image")

class FileSizeError(AppException):
    def __init__(self, message: str = "File too large"):
        super().__init__(message, 400, "file_too_large")

class ResourceNotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404, "not_found")

def create_error_response(code: str, message: str, details: dict = None):
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }

def http_exception_from_app_exception(exc: AppException):
    return HTTPException(
        status_code=exc.status_code,
        detail=create_error_response(exc.code, exc.message)
    )