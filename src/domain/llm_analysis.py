from dataclasses import dataclass, field


@dataclass(frozen=True)
class LLMAnalysis:
    """
    Result of the LLM analysis of a Listing.

    Invariants:
    - listing_id must match the Listing it was derived from
    - warmth_score is in [0.0, 10.0]: 0 = not warm at all, 10 = extremely warm
    - detected_defects is empty if no defects were found, never None
    - condition_mismatch is True when the seller's conditionGrade contradicts
      the description or images (e.g. "NEW" but defects visible)
    - material is None if the LLM could not determine it from available data
    - summary is always present — used to build the golden dataset UI
    """

    listing_id: str
    warmth_score: float
    detected_defects: list[str] = field(default_factory=list)
    condition_mismatch: bool = False
    material: str | None = None
    summary: str = ""
