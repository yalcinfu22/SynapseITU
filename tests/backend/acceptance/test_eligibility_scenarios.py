"""Acceptance scenarios of the Requirements Specification (Appendix A) for WBS-7.1.

The Gherkin runner (WBS-15.1) is not in the repository yet, so each scenario is a plain test
with its Given / When / Then steps.
"""

from datetime import date

import pytest

from app.eligibility.models import Education, Opportunity, Profile, Requirement
from app.eligibility.rules import Verdict
from app.eligibility.service import EligibilityService, InMemoryStore

TODAY = date(2026, 11, 27)


def must(rid, rule_type, **threshold):
    return Requirement(id=rid, rule_type=rule_type, threshold=threshold)


@pytest.fixture
def service():
    store = InMemoryStore(
        opportunities=[
            Opportunity(
                id="vision",
                title="Medical image segmentation assistant",
                description="PyTorch models for MRI segmentation.",
                institution="ITU",
                requirements=[must("r1", "skill", skill="PyTorch")],
            ),
            Opportunity(
                id="nlp",
                title="Türkçe doğal dil işleme stajyeri",
                description="Türkçe dil modelleri için veri seti.",
                institution="ITU",
                requirements=[must("r1", "language", code="tr", min="C1")],
            ),
            Opportunity(
                id="msc",
                title="MSc position in power systems",
                description="Grid stability research.",
                institution="Other University",
                requirements=[must("r1", "degree_level", min="bachelor")],
            ),
            Opportunity(
                id="closed", title="Closed vision position", description="PyTorch.", status="closed"
            ),
        ],
        profiles=[
            Profile(
                student_id="ayse",
                education=[
                    Education(degree_level="bachelor_student", field="Computer Engineering")
                ],
                skills=["Python", "PyTorch"],
            )
        ],
    )
    return EligibilityService(store, today=lambda: TODAY)


async def test_us32_filtered_eligibility_search(service):
    # Given a student profile and a set of must-have requirements
    # When the student searches with filters
    results = await service.search("ayse", filters={"institution": "ITU"}, eligible_only=True)
    # Then eligible opportunities are listed
    assert [r.opportunity.id for r in results.items] == ["vision"]
    assert all(r.verdict is Verdict.ELIGIBLE for r in results.items)


async def test_us33_unmet_requirement_is_shown_as_the_reason(service):
    # Given an opportunity whose must-have requirement I do not meet
    # When it appears in my results
    results = await service.search("ayse", query="power systems")
    # Then the unmet requirement is shown as its reason
    item = results.items[0]
    assert item.opportunity.id == "msc"
    assert item.verdict is Verdict.NOT_ELIGIBLE
    assert [(r.requirement_id, r.reason) for r in item.unmet] == [("r1", "degree_too_low")]


async def test_fr35_no_result_gives_a_hint(service):
    results = await service.search("ayse", query="astrophysics")
    assert results.items == [] and results.hint == "relax_filters"


async def test_fr35_turkish_query_without_turkish_letters(service):
    results = await service.search("ayse", query="dogal dil isleme")
    assert results.items[0].opportunity.id == "nlp"
    assert results.items[0].verdict is Verdict.CANNOT_CHECK  # no language data in the profile


async def test_closed_opportunities_are_not_in_the_search(service):
    results = await service.search("ayse", query="vision")
    assert "closed" not in [r.opportunity.id for r in results.items]


async def test_scfr37_eligible_pool_for_the_ai_search(service):
    # Given a student and opportunities of which only some are eligible for that student
    # When the AI search requests the student's eligible pool through the interface
    pool = await service.eligible_pool("ayse")
    # Then only the eligible opportunities are returned
    assert [o.id for o in pool] == ["vision"]
