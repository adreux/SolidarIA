from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Money:
    value: float
    currency: str


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
