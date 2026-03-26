from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from database import create_db_and_tables, init_default_data
from model_loader import model_loader
from exceptions import AppException, create_error_response
from routers import auth, patients, predict
from log import setup_logging

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application startup complete")
    
    # Create database tables
    create_db_and_tables()
    init_default_data()
    
    # Load ML model
    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, "models", "efficientnet_b0_best.h5")
    await model_loader.load_model(model_path)
    
    if not model_loader.is_loaded():
        print(f"Warning: Model failed to load - {model_loader.get_load_error()}")
    else:
        print("ML Model loaded successfully")
    
    yield
    
    # Shutdown
    print("Application shutdown")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - configured from environment
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.code, exc.message)
    )

# Include routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(predict.router)

# Serve frontend
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NeuroScan AI Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )