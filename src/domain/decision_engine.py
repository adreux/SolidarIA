from .listing import Listing
from .llm_analysis import LLMAnalysis
from .policy import Policy
from .recommendation import RecommandationLevel, Recommendation


class DecisionEngine:
    def __init__(self, policies: list[Policy]):
        self.policies = policies

    def make_decision(
        self, listing: Listing, llmanalysis: LLMAnalysis
    ) -> Recommendation:
        for policy in self.policies:
            result = policy.apply(listing, llmanalysis)
            if result == RecommandationLevel.SKIP:
                return Recommendation(
                    listing_id=listing.id,
                    level=RecommandationLevel.SKIP,
                    reason=f"Policy failed: '{policy.__class__.__name__}'",
                )
        return Recommendation(
            listing_id=listing.id,
            level=RecommandationLevel.INVESTIGATE,
            reason="All policies passed",
        )


class DecisionEngineFullPolicy:
    def __init__(self, policies: list[Policy]):
        self.policies = policies

    def make_decision(
        self, listing: Listing, llmanalysis: LLMAnalysis
    ) -> list[Recommendation]:
        results = []
        for policy in self.policies:
            result = policy.apply(listing, llmanalysis)
            if result == RecommandationLevel.SKIP:
                results.append(
                    Recommendation(
                        listing_id=listing.id,
                        level=RecommandationLevel.SKIP,
                        reason=f"Policy failed: '{policy.__class__.__name__}'",
                    )
                )
        if not results:
            return [
                Recommendation(
                    listing_id=listing.id,
                    level=RecommandationLevel.INVESTIGATE,
                    reason="All policies passed",
                )
            ]
        return results
