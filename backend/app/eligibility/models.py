"""Data the eligibility engine reads (WBS-7.1).

The fields follow the data contract of WBS-14.7 (docs/database-design/data-contract.md).
"""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel

# The rule vocabulary of the data contract.
RuleType = Literal["degree_level", "field_of_study", "skill", "language", "grade"]

# Ordered: a higher level meets a lower minimum.
DEGREE_LEVELS = ["bachelor_student", "bachelor", "master_student", "master", "phd_student", "phd"]
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class Requirement(BaseModel):
    id: str
    rule_type: RuleType
    threshold: dict[str, Any]
    must_have: bool = True
    weight: float = 1.0
    label: str = ""


class Opportunity(BaseModel):
    id: str
    title: str
    description: str
    institution: str | None = None
    status: Literal["draft", "open", "closed", "archived"] = "open"
    deadline: date | None = None
    requirements: list[Requirement] = []

    def search_text(self) -> str:
        return f"{self.title} {self.description} {self.institution or ''}"


class Education(BaseModel):
    degree_level: str | None = None
    field: str | None = None
    grade: float | None = None
    grade_scale: float | None = None


class Language(BaseModel):
    code: str
    level: str


class Profile(BaseModel):
    """An empty list means that the student did not give the data."""

    student_id: str
    education: list[Education] = []
    skills: list[str] = []
    languages: list[Language] = []
