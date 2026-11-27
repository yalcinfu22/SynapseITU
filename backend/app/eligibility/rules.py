"""One rule for each requirement type, and the verdict for one opportunity (FR-36)."""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum

from app.eligibility.models import CEFR_LEVELS, DEGREE_LEVELS, Opportunity, Profile, Requirement
from app.text import tokenize


class Status(StrEnum):
    MET = "met"
    NOT_MET = "not_met"
    CANNOT_CHECK = "cannot_check"


class Verdict(StrEnum):
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE = "not_eligible"
    CANNOT_CHECK = "cannot_check"


@dataclass(frozen=True)
class RuleResult:
    requirement_id: str
    must_have: bool
    status: Status
    reason: str | None = None  # a code; the web app shows the text in Turkish or English


MISSING = (Status.CANNOT_CHECK, "missing_profile_data")
MET = (Status.MET, None)


def _same(a: str, b: str) -> bool:
    return tokenize(a) == tokenize(b)


def _degree_level(t: dict, p: Profile):
    levels = [
        DEGREE_LEVELS.index(e.degree_level) for e in p.education if e.degree_level in DEGREE_LEVELS
    ]
    if not levels:
        return MISSING
    return (
        MET if max(levels) >= DEGREE_LEVELS.index(t["min"]) else (Status.NOT_MET, "degree_too_low")
    )


def _field_of_study(t: dict, p: Profile):
    fields = [e.field for e in p.education if e.field]
    if not fields:
        return MISSING
    ok = any(_same(f, allowed) for f in fields for allowed in t["fields"])
    return MET if ok else (Status.NOT_MET, "field_not_accepted")


def _skill(t: dict, p: Profile):
    if not p.skills:
        return MISSING
    return MET if any(_same(s, t["skill"]) for s in p.skills) else (Status.NOT_MET, "skill_missing")


def _language(t: dict, p: Profile):
    if not p.languages:
        return MISSING
    levels = [
        CEFR_LEVELS.index(lang.level)
        for lang in p.languages
        if lang.code.lower() == t["code"].lower()
    ]
    ok = bool(levels) and max(levels) >= CEFR_LEVELS.index(t["min"])
    return MET if ok else (Status.NOT_MET, "language_too_low")


def _grade(t: dict, p: Profile):
    graded = [e for e in p.education if e.grade is not None and e.grade_scale is not None]
    if not graded:
        return MISSING
    same_scale = [e.grade for e in graded if e.grade_scale == t["scale"]]
    if not same_scale:
        # The data contract compares grades only on the same scale.
        return (Status.CANNOT_CHECK, "grade_scale_differs")
    return MET if max(same_scale) >= t["min"] else (Status.NOT_MET, "grade_too_low")


RULES: dict[str, Callable[[dict, Profile], tuple[Status, str | None]]] = {
    "degree_level": _degree_level,
    "field_of_study": _field_of_study,
    "skill": _skill,
    "language": _language,
    "grade": _grade,
}


def check(requirement: Requirement, profile: Profile) -> RuleResult:
    status, reason = RULES[requirement.rule_type](requirement.threshold, profile)
    return RuleResult(requirement.id, requirement.must_have, status, reason)


@dataclass(frozen=True)
class Evaluation:
    opportunity: Opportunity
    verdict: Verdict
    results: list[RuleResult]
    blockers: list[str] = field(default_factory=list)  # "not_open", "deadline_passed"

    @property
    def unmet(self) -> list[RuleResult]:
        return [r for r in self.results if r.must_have and r.status is Status.NOT_MET]

    @property
    def cannot_check(self) -> list[RuleResult]:
        return [r for r in self.results if r.must_have and r.status is Status.CANNOT_CHECK]

    @property
    def missing_plus(self) -> list[RuleResult]:
        return [r for r in self.results if not r.must_have and r.status is not Status.MET]


def evaluate(opportunity: Opportunity, profile: Profile, today: date) -> Evaluation:
    """Plus requirements never change the verdict."""
    results = [check(r, profile) for r in opportunity.requirements]
    blockers = []
    if opportunity.status != "open":
        blockers.append("not_open")
    if opportunity.deadline and opportunity.deadline < today:
        blockers.append("deadline_passed")

    evaluation = Evaluation(opportunity, Verdict.ELIGIBLE, results, blockers)
    if blockers or evaluation.unmet:
        verdict = Verdict.NOT_ELIGIBLE
    elif evaluation.cannot_check:
        verdict = Verdict.CANNOT_CHECK
    else:
        return evaluation
    return Evaluation(opportunity, verdict, results, blockers)
