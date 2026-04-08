from abc import ABC, abstractmethod

from .listing import Listing
from .llm_analysis import LLMAnalysis
from .recommendation import RecommandationLevel


class Policy(ABC):
    """Abstract base class for all domain policies.

    Invariants:
    - apply() returns None if the listing passes the policy
    - apply() returns a RecommandationLevel if the listing is blocked
    - policies are stateless except for their configuration thresholds
    - policies never call external services or access infrastructure
    """

    @abstractmethod
    def apply(
        self, listing: Listing, llmanalysis: LLMAnalysis
    ) -> RecommandationLevel | None:
        pass


class PricePolicy(Policy):
    def __init__(self, max_price: float = 30.0):
        self.max_price = max_price

    def apply(
        self, listing: Listing, llmanalysis: LLMAnalysis
    ) -> RecommandationLevel | None:
        price = listing.price.total_eur
        if price < self.max_price:
            return None
        else:
            return RecommandationLevel.SKIP


class SellerFeedbackPolicy(Policy):
    def __init__(self, min_feedback_percentage: float = 85.0):
        self.min_feedback_percentage = min_feedback_percentage

    def apply(
        self, listing: Listing, llmanalysis: LLMAnalysis
    ) -> RecommandationLevel | None:
        if listing.seller_feedback_percentage > self.min_feedback_percentage:
            return None
        else:
            return RecommandationLevel.SKIP


class WarmthPolicy(Policy):
    def __init__(self, min_warmth_score: float = 1.0):
        self.min_warmth_score = min_warmth_score

    def apply(
        self, listing: Listing, llmanalysis: LLMAnalysis
    ) -> RecommandationLevel | None:
        if llmanalysis.warmth_score > self.min_warmth_score:
            return None
        else:
            return RecommandationLevel.SKIP
