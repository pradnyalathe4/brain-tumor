from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import create_db_and_tables
from routers import auth, patients, scans, predict
from security import get_current_doctor

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="NeuroScan AI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(scans.router, prefix="/api/scans", tags=["scans"])
app.include_router(predict.router, prefix="/api", tags=["predict"])

@app.get("/")
def root(request: Request):
    return RedirectResponse("/dashboard")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/patients")
def patients_page(request: Request):
    return templates.TemplateResponse("patients.html", {"request": request})

@app.get("/patients/{patient_id}")
def patient_detail_page(request: Request, patient_id: str):
    return templates.TemplateResponse("patient_detail.html", {"request": request, "patient_id": patient_id})

@app.get("/predict")
def predict_page(request: Request):
    return templates.TemplateResponse("predict.html", {"request": request})

@app.get("/scans/{scan_id}")
def scan_detail_page(request: Request, scan_id: str):
    return templates.TemplateResponse("scan_detail.html", {"request": request, "scan_id": scan_id})

@app.get("/404")
def not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
