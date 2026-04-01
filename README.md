# NeuroScan AI — MRI Brain Tumor Classification

A FastAPI-based web application for MRI brain tumor classification using EfficientNet-B0 transfer learning. Local-only, no external APIs, no Docker.

## Quick Start

```bash
# 1. Clone and navigate
git clone <repo-url>
cd mri-brain-tumor-classification-efficientnet

# 2. Create virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and set JWT_SECRET to a random string

# 5. Create uploads folder
mkdir uploads

# 6. Run the application
python main.py
```

Open http://localhost:8000

Demo: Register a new doctor account to get started.

## Features

- **JWT Authentication** - Secure login/register for medical professionals
- **Patient Management** - Create, view, and manage patient records
- **MRI Scan Upload** - Upload brain MRI images for analysis
- **Tumor Classification** - EfficientNet-B0 based classification (Glioma, Meningioma, Pituitary, No Tumor)
- **Dashboard** - Statistics and recent scans overview
- **Local Storage** - SQLite database, no external services

## Tech Stack

- Backend: FastAPI + Uvicorn
- ML: TensorFlow 2.x + EfficientNet-B0
- Database: SQLite via SQLModel
- Auth: JWT (python-jose) + bcrypt (passlib)
- Templates: Jinja2
- Frontend: Vanilla JS + CSS

## Project Structure

```
├── main.py                 # FastAPI entry point
├── config.py              # Settings via pydantic-settings
├── database.py           # SQLite + SQLModel
├── security.py           # JWT + bcrypt
├── routers/
│   ├── auth.py           # Register, Login, Me
│   ├── patients.py       # CRUD patients
│   ├── scans.py          # List scans, stats
│   └── predict.py        # Upload MRI → prediction
├── models/
│   ├── db_models.py      # Doctor, Patient, Scan tables
│   └── ml_model.py       # EfficientNet predictor
├── templates/            # Jinja2 HTML templates
├── static/
│   ├── css/app.css       # All styles
│   └── js/               # Client-side JS
├── uploads/              # Uploaded MRI images
├── tests/                # Pytest tests
├── requirements.txt
└── .env.example
```

## Notes

- **No trained model?** The app runs in demo mode with realistic mock predictions.
- **To use a real model:** Place `efficientnet_brain_tumor.h5` in the `models/` folder.
- All data is stored locally in `neuroscan.db`.

## License

MIT
