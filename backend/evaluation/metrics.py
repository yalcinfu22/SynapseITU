"""Ranking metrics.

``precision_at_k`` is the D-04 / NFR-26 acceptance metric. It is normalised by
``min(k, relevant candidates)`` so that a query with fewer than ``k`` relevant eligible
opportunities can still reach 1.0 (a plain hits/k would cap such a query below 1 for every
system and hide differences). Queries without any relevant candidate are excluded (NaN).
``mrr_at_k`` is reported for diagnosis only.
"""

import math
from collections.abc import Sequence


def precision_at_k(
    ranked: Sequence[str], relevant: set[str], candidates: set[str], k: int = 5
) -> float:
    reachable = relevant & candidates
    if not reachable:
        return math.nan
    return sum(1 for d in ranked[:k] if d in reachable) / min(k, len(reachable))


def mrr_at_k(ranked: Sequence[str], relevant: set[str], k: int = 10) -> float:
    for i, d in enumerate(ranked[:k], start=1):
        if d in relevant:
            return 1.0 / i
    return 0.0


def mean(values: Sequence[float]) -> float:
    vals = [v for v in values if not math.isnan(v)]
    return sum(vals) / len(vals) if vals else math.nan
