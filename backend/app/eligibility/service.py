"""Eligibility search (FR-35, FR-36) and the eligible pool for the AI search (FR-37)."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from app.eligibility.models import Opportunity, Profile
from app.eligibility.rules import Evaluation, Verdict, evaluate
from app.text import tokenize


class Store(Protocol):
    """Data access. The database version comes with WBS-14.3."""

    async def open_opportunities(self) -> list[Opportunity]: ...

    async def profile(self, student_id: str) -> Profile | None: ...


class InMemoryStore:
    """For tests and local development until the database is ready."""

    def __init__(self, opportunities: list[Opportunity], profiles: list[Profile]) -> None:
        self._opportunities = opportunities
        self._profiles = {p.student_id: p for p in profiles}

    async def open_opportunities(self) -> list[Opportunity]:
        # Closed and archived opportunities are not in the eligibility search (FR-26).
        return [o for o in self._opportunities if o.status == "open"]

    async def profile(self, student_id: str) -> Profile | None:
        return self._profiles.get(student_id)


@dataclass(frozen=True)
class SearchResult:
    items: list[Evaluation]
    hint: str | None = None  # "relax_filters" when there is no result (FR-35)


class EligibilityService:
    def __init__(self, store: Store, today: Callable[[], date] = date.today) -> None:
        self._store = store
        self._today = today

    async def _profile(self, student_id: str) -> Profile:
        profile = await self._store.profile(student_id)
        if profile is None:
            raise LookupError(f"no profile for student {student_id}")
        return profile

    async def search(
        self,
        student_id: str,
        query: str = "",
        filters: dict[str, str] | None = None,
        eligible_only: bool = False,
    ) -> SearchResult:
        profile = await self._profile(student_id)
        opportunities = await self._store.open_opportunities()

        institution = (filters or {}).get("institution")
        if institution:
            opportunities = [o for o in opportunities if o.institution == institution]

        terms = set(tokenize(query))
        if terms:
            scored = [(len(terms & set(tokenize(o.search_text()))), o) for o in opportunities]
            opportunities = [o for score, o in sorted(scored, key=lambda x: -x[0]) if score > 0]

        today = self._today()
        items = [evaluate(o, profile, today) for o in opportunities]
        if eligible_only:
            items = [e for e in items if e.verdict is Verdict.ELIGIBLE]
        return SearchResult(items, None if items else "relax_filters")

    async def eligible_pool(self, student_id: str) -> list[Opportunity]:
        """The one interface for the AI search (FR-37). Only eligible opportunities."""
        profile = await self._profile(student_id)
        today = self._today()
        return [
            o
            for o in await self._store.open_opportunities()
            if evaluate(o, profile, today).verdict is Verdict.ELIGIBLE
        ]
