from datetime import date

from app.eligibility.models import Education, Opportunity, Profile, Requirement
from app.eligibility.rules import Verdict, evaluate

TODAY = date(2026, 11, 27)
STUDENT = Profile(
    student_id="s1",
    education=[Education(degree_level="bachelor_student", field="Computer Engineering")],
    skills=["Python"],
)


def opportunity(*requirements, status="open", deadline=None) -> Opportunity:
    return Opportunity(
        id="o1",
        title="t",
        description="d",
        status=status,
        deadline=deadline,
        requirements=list(requirements),
    )


def must(rid, rule_type, **threshold):
    return Requirement(id=rid, rule_type=rule_type, threshold=threshold)


def plus(rid, rule_type, **threshold):
    return Requirement(id=rid, rule_type=rule_type, threshold=threshold, must_have=False)


def test_all_must_haves_met_is_eligible():
    result = evaluate(opportunity(must("a", "skill", skill="Python")), STUDENT, TODAY)
    assert result.verdict is Verdict.ELIGIBLE


def test_one_reason_for_each_unmet_must_have():
    result = evaluate(
        opportunity(
            must("a", "degree_level", min="master"),
            must("b", "skill", skill="Rust"),
            must("c", "skill", skill="Python"),
        ),
        STUDENT,
        TODAY,
    )
    assert result.verdict is Verdict.NOT_ELIGIBLE
    assert [r.requirement_id for r in result.unmet] == ["a", "b"]


def test_plus_requirement_does_not_change_the_verdict():
    result = evaluate(opportunity(plus("p", "skill", skill="Rust")), STUDENT, TODAY)
    assert result.verdict is Verdict.ELIGIBLE
    assert [r.requirement_id for r in result.missing_plus] == ["p"]


def test_missing_data_gives_cannot_be_checked():
    result = evaluate(opportunity(must("g", "grade", min=3.0, scale=4.0)), STUDENT, TODAY)
    assert result.verdict is Verdict.CANNOT_CHECK
    assert [r.requirement_id for r in result.cannot_check] == ["g"]


def test_closed_or_past_deadline_is_not_eligible():
    closed = evaluate(opportunity(status="closed"), STUDENT, TODAY)
    late = evaluate(opportunity(deadline=date(2026, 11, 1)), STUDENT, TODAY)
    assert closed.verdict is late.verdict is Verdict.NOT_ELIGIBLE
    assert closed.blockers == ["not_open"] and late.blockers == ["deadline_passed"]


def test_deadline_today_is_still_eligible():
    assert evaluate(opportunity(deadline=TODAY), STUDENT, TODAY).verdict is Verdict.ELIGIBLE
