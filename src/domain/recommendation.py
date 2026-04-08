from dataclasses import dataclass
from enum import Enum


class RecommandationLevel(Enum):
    BUY = "BUY"
    INVESTIGATE = "INVESTIGATE"
    SKIP = "SKIP"


@dataclass(frozen=True)
class Recommendation:
    """
    A recommendation for a listing, based on the LLM analysis.

    Invariants:
    - listing_id must match the Listing it was derived from
    - level is one of "BUY", "INVESTIGATE", "SKIP"
    - reason is a human-readable explanation for the recommendation
    """

    listing_id: str
    level: RecommandationLevel
    reason: str
