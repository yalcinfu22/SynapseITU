"""Public API contracts for the dummy university records."""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class UniversityRecord(BaseModel):
    """Fields shared by all records imported into SynapseITU."""

    id: str
    university_id: str
    name: str
    description: str
    updated_at: datetime
    source_url: str


class Program(UniversityRecord):
    department: str
    degree_level: Literal["BSc", "MSc", "PhD"]


class Lab(UniversityRecord):
    research_areas: list[str] = Field(default_factory=list)


class Position(UniversityRecord):
    lab_id: str
    program_id: str | None = None
    position_type: Literal["Research Assistant", "Internship", "PhD"]
    status: Literal["open", "closed"]
    application_deadline: date
