from .listing import Listing
from .llm_analysis import LLMAnalysis
from .policy import Policy
from .recommendation import RecommandationLevel, Recommendation


class DecisionEngine:
    """Evaluates a listing against a list of policies and returns the first blocking recommendation.

    Invariants:
    - stops at the first policy that returns SKIP (short-circuit)
    - returns INVESTIGATE if all policies pass
    - never returns BUY — the final purchase decision belongs to the user
    """

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
    """Evaluates a listing against all policies and collects every blocking recommendation.

    Invariants:
    - runs all policies regardless of intermediate results (no short-circuit)
    - returns one Recommendation per failing policy
    - returns a single INVESTIGATE if all policies pass
    - designed for golden dataset construction — preserves full failure context
    """

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
