from enum import Enum
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional
import json
from typing import List, Union

class RequirementGroupType(str, Enum):
    any_of = "any_of"              # one of the listed items
    category_any_of = "category_any_of"  # one or more from a category

class PrimaryDomain(str, Enum):
    web = "Web"
    cloud = "Cloud"
    ai = "AI"
    data = "Data"
    mobile = "Mobile"
    devops = "DevOps"
    security = "Security"
    enterprise = "Enterprise"
    frontend = "Frontend"
    fullstack = "Fullstack"
    qa = "QA"
    backend="Backend"
    general = "General"

class SeniorityLevel(str, Enum):
    junior = "Junior"
    mid = "Mid"
    senior = "Senior"
    lead = "Lead"


class SkillSource(str, Enum):
    explicit = "explicit"
    inferred = "inferred"


class RequirementLevel(str, Enum):
    hard = "hard"
    soft = "soft"


class SkillTypeHint(str, Enum):
    programming = "programming"
    framework = "framework"
    cloud = "cloud"
    database = "database"
    tool = "tool"
    platform = "platform"
    methodology = "methodology"
    other = "other"


class ExpectedEvidence(str, Enum):
    resume_skill = "resume_skill"
    experience_role = "experience_role"
    project = "project"
    implicit = "implicit"



class SkillRequirement(BaseModel):
    raw_skill: str = Field(..., min_length=1)
    source: SkillSource
    requirement_level: RequirementLevel
    skill_type_hint: SkillTypeHint
    min_months: Optional[int] = Field(None, ge=0, le=240)
    skill_group_id: Optional[str] = ""
    expected_evidence: ExpectedEvidence

    @field_validator("min_months", mode="before")
    @classmethod
    def default_min_months(cls, v):
        if v is None:
            return 0
        return v

    @field_validator("raw_skill")
    @classmethod
    def normalize_raw_skill(cls, v: str) -> str:
        return v.strip()

    @field_validator("skill_group_id")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

class JobMetadata(BaseModel):
    primary_domain: PrimaryDomain
    seniority_level: SeniorityLevel


class CategoryRequirement(BaseModel):
    group_id: str = Field(..., min_length=3)
    group_type: RequirementGroupType = RequirementGroupType.category_any_of

    # This MUST map to MasterSkills.Category
    category: str = Field(..., min_length=3)

    # Quantifier
    min_required: int = Field(..., ge=1, le=10)

    # Examples mentioned in JD (non-mandatory, explanatory)
    example_skills: List[str] = Field(default_factory=list)

    requirement_level: RequirementLevel
    source: SkillSource

    @field_validator("example_skills", mode="before")
    @classmethod
    def normalize_examples(cls, v):
        if not v:
            return []
        return [s.strip() for s in v if s.strip()]

Requirement = Union[SkillRequirement, CategoryRequirement]

class JobSkillProfile(BaseModel):
    role_context: str = Field(..., min_length=10)
    job_metadata: JobMetadata

    # Mixed requirement list
    requirements: List[Requirement]   

    @field_validator("requirements")
    @classmethod
    def ensure_at_least_one_hard_requirement(cls, v):
        if not any(r.requirement_level == RequirementLevel.hard for r in v):
            raise ValueError("At least one hard requirement is required")
        return v