"""WBS-7.1 DoD: each rule type of the data contract (WBS-14.7) has a rule test."""

import pytest

from app.eligibility.models import Education, Language, Profile, Requirement, RuleType
from app.eligibility.rules import RULES, Status, check

PROFILE = Profile(
    student_id="s1",
    education=[
        Education(
            degree_level="bachelor_student",
            field="Bilgisayar Mühendisliği",
            grade=3.1,
            grade_scale=4.0,
        )
    ],
    skills=["Python", "PyTorch"],
    languages=[Language(code="en", level="B2")],
)
EMPTY = Profile(student_id="s2")


def req(rule_type: RuleType, **threshold) -> Requirement:
    return Requirement(id="r1", rule_type=rule_type, threshold=threshold)


CASES = [
    (req("degree_level", min="bachelor_student"), Status.MET),
    (req("degree_level", min="master"), Status.NOT_MET),
    (req("field_of_study", fields=["bilgisayar muhendisligi"]), Status.MET),
    (req("field_of_study", fields=["Electrical Engineering"]), Status.NOT_MET),
    (req("skill", skill="pytorch"), Status.MET),
    (req("skill", skill="ROS 2"), Status.NOT_MET),
    (req("language", code="en", min="B2"), Status.MET),
    (req("language", code="en", min="C1"), Status.NOT_MET),
    (req("language", code="de", min="A1"), Status.NOT_MET),
    (req("grade", min=3.0, scale=4.0), Status.MET),
    (req("grade", min=3.5, scale=4.0), Status.NOT_MET),
]


def test_each_rule_type_has_a_rule_and_a_test():
    rule_types = set(RuleType.__args__)
    assert set(RULES) == rule_types
    assert {r.rule_type for r, _ in CASES} == rule_types


@pytest.mark.parametrize(("requirement", "expected"), CASES)
def test_rule_against_a_full_profile(requirement, expected):
    result = check(requirement, PROFILE)
    assert result.status is expected
    assert (result.reason is None) == (expected is Status.MET)


@pytest.mark.parametrize("rule_type", RuleType.__args__)
def test_missing_profile_data_cannot_be_checked(rule_type):
    requirement = next(r for r, _ in CASES if r.rule_type == rule_type)
    result = check(requirement, EMPTY)
    assert result.status is Status.CANNOT_CHECK
    assert result.reason == "missing_profile_data"


def test_grade_on_another_scale_cannot_be_checked():
    result = check(req("grade", min=75, scale=100), PROFILE)
    assert result.status is Status.CANNOT_CHECK
