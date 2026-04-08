import pytest

from src.domain.decision_engine import DecisionEngine, DecisionEngineFullPolicy
from src.domain.listing import ConditionGrade, Listing, Money
from src.domain.llm_analysis import LLMAnalysis
from src.domain.policy import PricePolicy, SellerFeedbackPolicy, WarmthPolicy
from src.domain.recommendation import RecommandationLevel


@pytest.fixture
def good_listing():
    return Listing(
        id="v1|123|0",
        title="Manteau laine",
        price=Money(value=20.0, currency="EUR"),
        shipping_cost=5.0,
        condition=ConditionGrade.VERY_GOOD,
        condition_description=None,
        description=None,
        image_urls=[],
        seller_feedback_percentage=95.0,
        accepts_returns=True,
    )


@pytest.fixture
def good_analysis():
    return LLMAnalysis(
        listing_id="v1|123|0",
        warmth_score=8.0,
    )


class TestDecisionEngine:
    def test_all_policies_pass_returns_investigate(self, good_listing, good_analysis):
        engine = DecisionEngine(
            policies=[PricePolicy(), SellerFeedbackPolicy(), WarmthPolicy()]
        )
        result = engine.make_decision(good_listing, good_analysis)
        assert result.level == RecommandationLevel.INVESTIGATE

    def test_price_policy_overrides_llm(self, good_analysis):
        expensive_listing = Listing(
            id="v1|999|0",
            title="Manteau cher",
            price=Money(value=50.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.NEW,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=99.0,
            accepts_returns=True,
        )
        engine = DecisionEngine(policies=[PricePolicy(max_price=30.0)])
        result = engine.make_decision(expensive_listing, good_analysis)
        assert result.level == RecommandationLevel.SKIP

    def test_seller_feedback_policy_overrides_llm(self, good_listing, good_analysis):
        bad_seller_listing = Listing(
            id="v1|456|0",
            title="Manteau vendeur douteux",
            price=Money(value=20.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=70.0,
            accepts_returns=True,
        )
        engine = DecisionEngine(
            policies=[SellerFeedbackPolicy(min_feedback_percentage=85.0)]
        )
        result = engine.make_decision(bad_seller_listing, good_analysis)
        assert result.level == RecommandationLevel.SKIP

    def test_stops_at_first_failing_policy(self, good_analysis):
        expensive_bad_listing = Listing(
            id="v1|789|0",
            title="Manteau cher et mauvais vendeur",
            price=Money(value=50.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=70.0,
            accepts_returns=False,
        )
        engine = DecisionEngine(policies=[PricePolicy(), SellerFeedbackPolicy()])
        result = engine.make_decision(expensive_bad_listing, good_analysis)
        assert result.level == RecommandationLevel.SKIP
        assert "PricePolicy" in result.reason


class TestDecisionEngineFullPolicy:
    def test_all_policies_pass_returns_investigate(self, good_listing, good_analysis):
        engine = DecisionEngineFullPolicy(
            policies=[PricePolicy(), SellerFeedbackPolicy(), WarmthPolicy()]
        )
        results = engine.make_decision(good_listing, good_analysis)
        assert len(results) == 1
        assert results[0].level == RecommandationLevel.INVESTIGATE

    def test_collects_all_failing_policies(self, good_analysis):
        bad_listing = Listing(
            id="v1|789|0",
            title="Manteau cher et mauvais vendeur",
            price=Money(value=50.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=70.0,
            accepts_returns=False,
        )
        engine = DecisionEngineFullPolicy(
            policies=[PricePolicy(), SellerFeedbackPolicy()]
        )
        results = engine.make_decision(bad_listing, good_analysis)
        assert len(results) == 2
        assert all(r.level == RecommandationLevel.SKIP for r in results)
        reasons = [r.reason for r in results]
        assert any("PricePolicy" in r for r in reasons)
        assert any("SellerFeedbackPolicy" in r for r in reasons)
