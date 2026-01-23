"""
Pydantic schemas for validating raw experience extraction from LLM responses.

This module defines the data models for the extract_raw_experience function,
ensuring structured and validated output from LLM calls.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class ProgrammingSkills(BaseModel):
    """Programming-related skills and technologies."""
    languages: List[str] = Field(default_factory=list, description="Programming languages e.g., ['Python', 'JavaScript'], return [] if none")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks e.g., ['Django', 'React', '.NET', 'Angular'], return [] if none")
    tools: List[str] = Field(default_factory=list, description="Development tools e.g., ['Docker', 'Kubernetes', 'vite', 'webpack'], return [] if none")
    libraries: List[str] = Field(default_factory=list, description="Libraries e.g., ['NumPy', 'Pandas', 'TensorFlow'], return [] if none")


class MethodologyItem(BaseModel):
    """Individual methodology with its associated skills."""
    type: str = Field(description="Methodology type e.g., 'Agile', 'Waterfall'")
    skills: List[str] = Field(default_factory=list, description="Skills within this methodology e.g., ['Scrum', 'Kanban'], return [] if none")


class SoftwareDevelopmentSkills(BaseModel):
    """Software development practices and processes."""
    methodologies: List[MethodologyItem] = Field(default_factory=list, description="Development methodologies with associated skills, return [] if none")
    version_control: List[str] = Field(default_factory=list, description="Version control systems e.g., ['Git', 'SVN'], return [] if none")
    testing: List[str] = Field(default_factory=list, description="Testing approaches e.g., ['unit testing', 'integration testing'], return [] if none")
    continuous_integration: List[str] = Field(default_factory=list, description="CI tools e.g., ['Jenkins', 'Travis CI'], return [] if none")


class ArchitectureSkills(BaseModel):
    """Architectural patterns and cloud services."""
    design_patterns: List[str] = Field(default_factory=list, description="Design patterns e.g., ['MVC', 'Singleton', 'Microservices', 'Event Driven'], return [] if none")
    cloud_services: List[str] = Field(default_factory=list, description="Cloud platforms e.g., ['AWS', 'Azure', 'GCP'], return [] if none")


class DataManagementSkills(BaseModel):
    """Data-related technologies and platforms."""
    databases: List[str] = Field(default_factory=list, description="Databases e.g., ['MySQL', 'MongoDB', 'PostgreSQL'], return [] if none")
    data_warehousing: List[str] = Field(default_factory=list, description="Data warehousing solutions e.g., ['Redshift', 'BigQuery'], return [] if none")
    data_analytics: List[str] = Field(default_factory=list, description="Analytics tools e.g., ['Tableau', 'Power BI'], return [] if none")


class SecuritySkills(BaseModel):
    """Security practices and tools."""
    practices: List[str] = Field(default_factory=list, description="Security practices e.g., ['encryption', 'penetration testing', 'authentication', 'role based access control'], return [] if none")
    tools: List[str] = Field(default_factory=list, description="Security tools e.g., ['Nessus', 'Wireshark', 'Owasp ZAP', 'Burp Suite'], return [] if none")


class Skills(BaseModel):
    """Comprehensive skills breakdown across all categories."""
    programming: ProgrammingSkills = Field(default_factory=ProgrammingSkills)
    software_development: SoftwareDevelopmentSkills = Field(default_factory=SoftwareDevelopmentSkills)
    architecture: ArchitectureSkills = Field(default_factory=ArchitectureSkills)
    data_management: DataManagementSkills = Field(default_factory=DataManagementSkills)
    security: SecuritySkills = Field(default_factory=SecuritySkills)


DomainType = Literal[
    "frontend", "backend", "fullstack", "devops", "data", "mobile",
    "other", "cloud", "UI/UX", "AI/ML", "security", "QA"
]

class ExtractedSkill(BaseModel):
    raw_name: str                     # "ASP.NET Core"    
    source: Literal[
        "technology_list",
        "skills_section",
        "responsibility",
        "implicit"
    ]
    confidence: float                 # 0.0 – 1.0


class RawExperienceItem(BaseModel):
    """
    Single work experience entry extracted from a resume.

    Represents one job/role with all its associated details including dates,
    technologies, domains, skills, and responsibilities.
    """
    job_title: str = Field(description="Job title")
    organization: Optional[str] = Field(default=None, description="Organization or company name")
    start_date_raw: Optional[str] = Field(default=None, description="Start date as found in text or inferred")
    end_date_raw: Optional[str] = Field(
        default=None,
        description="End date as found, 'Present' for ongoing roles, or null"
    )
    technologies: List[str] = Field(default_factory=list, description="List of technologies used, return [] if none")
    domains: List[DomainType] = Field(
        min_length=1,
        description="Domain(s) of the role from fixed choices"
    )
    skills: Skills = Field(default_factory=Skills, description="Detailed skills breakdown")
    responsibilities: List[str] = Field(default_factory=list, description="List of responsibilities, return [] if none")
    extracted_skills: List[ExtractedSkill] = Field(
        default_factory=list,
        description="Normalized skill mentions aligned with MasterSkills"
    )

# Type alias for the response (it's a list of experience items)
RawExperienceResponse = List[RawExperienceItem]
