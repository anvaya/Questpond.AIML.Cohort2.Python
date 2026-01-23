"""
FastAPI application for ATS Web Service
"""
import sys
import pathlib
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import ValidationError
import uvicorn

# Add parent directory to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from WebServer.models import (
    JobResponse, JobSubmitResponse, EmployerJobRequest,
    JobType, JobStatus
)
from WebServer.database import JobRepository
from WebServer.job_executor import get_executor

# Create FastAPI app
app = FastAPI(
    title="ATS Web API",
    description="AI-powered Applicant Tracking System - Proof of Concept",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize repositories
job_repo = JobRepository()


# --- API Endpoints ---

@app.post("/jobs/candidate", response_model=JobSubmitResponse)
async def submit_candidate_job(file: UploadFile = File(...)):
    """
    Submit a candidate resume processing job.

    Uploads a PDF resume and processes it asynchronously.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'): # type: ignore
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file to temp location
    temp_dir = pathlib.Path(__file__).parent.parent / "temp"
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / file.filename # type: ignore
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Create job
    input_data = {
        "file_path": str(file_path),
        "filename": file.filename
    }

    job_id = job_repo.create_job(
        job_type="candidate",
        input_data=input_data
    )

    # Submit to background executor
    executor = get_executor()

    def update_callback(job_id, status, progress, message, result=None, error_message=None):
        job_repo.update_job_status(
            job_id=job_id,
            status=status,
            progress=progress,
            message=message,
            result=result,
            error_message=error_message
        )

    executor.submit_candidate_job(job_id, str(file_path), update_callback)

    return JobSubmitResponse(job_id=job_id)


@app.post("/jobs/employer", response_model=JobSubmitResponse)
async def submit_employer_job(request: EmployerJobRequest):
    """
    Submit an employer matching job.

    Takes a job description and finds matching candidates.
    """
    # Validate JD length
    if len(request.job_description.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please provide more details."
        )

    # Create job
    input_data = {
        "job_description": request.job_description
    }

    job_id = job_repo.create_job(
        job_type="employer",
        input_data=input_data
    )

    # Submit to background executor
    executor = get_executor()

    def update_callback(job_id, status, progress, message, result=None, error_message=None):
        job_repo.update_job_status(
            job_id=job_id,
            status=status,
            progress=progress,
            message=message,
            result=result,
            error_message=error_message
        )

    executor.submit_employer_job(job_id, request.job_description, update_callback)

    return JobSubmitResponse(job_id=job_id)


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Get the status of a job.

    Returns current progress, status, and results if completed.
    """
    job = job_repo.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        return JobResponse(**job)
    except ValidationError:
        raise HTTPException(status_code=500, detail="Invalid job data")


@app.get("/")
async def root():
    """
    Root endpoint - returns API info.
    """
    return {
        "name": "ATS Web API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "candidate_job": "POST /jobs/candidate",
            "employer_job": "POST /jobs/employer",
            "job_status": "GET /jobs/{job_id}"
        }
    }


# --- Serve React Frontend (Production) ---

# Mount static files directory for React build output
# frontend_build_path = pathlib.Path(__file__).parent.parent / "frontend" / "dist"
# if frontend_build_path.exists():
#     app.mount("/assets", StaticFiles(directory=str(frontend_build_path / "assets")), name="assets")
#
#     @app.get("/{full_path:path}")
#     async def serve_react_app(full_path: str):
#         file_path = frontend_build_path / full_path
#         if file_path.exists() and file_path.is_file():
#             return FileResponse(file_path)
#         return FileResponse(frontend_build_path / "index.html")


# --- Run Server ---
if __name__ == "__main__":
    import shutil

    uvicorn.run(
        "WebServer.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
