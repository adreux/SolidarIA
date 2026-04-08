from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Money:
    """Immutable monetary value with currency.

    Invariants:
    - value is always positive
    - currency is an ISO 4217 code (e.g. "EUR", "USD")
    - conversion is only supported for EUR at this stage
    """

    value: float
    currency: str

    @property
    def total_eur(self) -> float:
        if self.currency == "EUR":
            return self.value
        raise ValueError(f"Conversion from {self.currency} not supported")


class ConditionGrade(Enum):
    NEW = "NEW"
    VERY_GOOD = "VERY_GOOD"
    GOOD = "GOOD"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_ebay_id(cls, ebay_id: str) -> "ConditionGrade":
        mapping = {"1000": cls.NEW, "3000": cls.VERY_GOOD, "5000": cls.GOOD}
        return mapping.get(ebay_id, cls.UNKNOWN)


@dataclass(frozen=True)
class Listing:
    """Core domain entity representing a coat listing, independent of any external source.

    Invariants:
    - id uniquely identifies the listing
    - price and shipping_cost are always positive
    - seller_feedback_percentage is in [0.0, 100.0]
    - image_urls may be empty but never None
    """

    id: str
    title: str
    price: Money
    shipping_cost: float
    condition: ConditionGrade
    condition_description: str | None
    description: str | None
    image_urls: list[str]
    seller_feedback_percentage: float
    accepts_returns: bool
