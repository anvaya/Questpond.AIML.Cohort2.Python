"""
Data models for the ATS Web API
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal, Any, Dict
from enum import Enum


class JobType(str, Enum):
    CANDIDATE = "candidate"
    EMPLOYER = "employer"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    id: str
    type: JobType
    status: JobStatus
    progress: int = 0
    message: str = ""
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    error_message: Optional[str] = None


class JobSubmitResponse(BaseModel):
    job_id: str


class CandidateJobRequest(BaseModel):
    # File will be uploaded via multipart/form-data, this is for reference
    pass


class EmployerJobRequest(BaseModel):
    job_description: str = Field(..., min_length=50, description="Plain text job description")


# Result models
class CandidateIdentity(BaseModel):
    full_name: str
    linkedin: Optional[str] = None
    github: Optional[str] = None


class CandidateRole(BaseModel):
    title: str
    verified_duration: int
    raw_technologies: list[str]
    domains: list[str]


class CandidateProfileResult(BaseModel):
    identity: CandidateIdentity
    candidate_roles: list[CandidateRole]


class CandidateJobResult(BaseModel):
    profile: CandidateProfileResult


class MatchCandidate(BaseModel):
    name: str
    score: float
    matches: list[str]
    confidence: str


class EmployerJobResult(BaseModel):
    matches: list[MatchCandidate]
