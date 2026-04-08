import pytest

from src.domain.listing import ConditionGrade, Listing, Money
from src.domain.llm_analysis import LLMAnalysis
from src.domain.policy import PricePolicy, SellerFeedbackPolicy, WarmthPolicy
from src.domain.recommendation import RecommandationLevel


@pytest.fixture
def base_listing():
    return Listing(
        id="v1|123|0",
        title="Manteau test",
        price=Money(value=20.0, currency="EUR"),
        shipping_cost=0.0,
        condition=ConditionGrade.GOOD,
        condition_description=None,
        description=None,
        image_urls=[],
        seller_feedback_percentage=95.0,
        accepts_returns=True,
    )


@pytest.fixture
def base_analysis():
    return LLMAnalysis(listing_id="v1|123|0", warmth_score=5.0)


class TestPricePolicy:
    def test_below_threshold_returns_none(self, base_listing, base_analysis):
        policy = PricePolicy(max_price=30.0)
        assert policy.apply(base_listing, base_analysis) is None

    def test_above_threshold_returns_skip(self, base_analysis):
        listing = Listing(
            id="v1|123|0",
            title="Manteau cher",
            price=Money(value=31.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=95.0,
            accepts_returns=True,
        )
        policy = PricePolicy(max_price=30.0)
        assert policy.apply(listing, base_analysis) == RecommandationLevel.SKIP

    def test_exactly_at_threshold_returns_skip(self, base_analysis):
        listing = Listing(
            id="v1|123|0",
            title="Manteau seuil",
            price=Money(value=30.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=95.0,
            accepts_returns=True,
        )
        policy = PricePolicy(max_price=30.0)
        assert policy.apply(listing, base_analysis) == RecommandationLevel.SKIP


class TestSellerFeedbackPolicy:
    def test_above_threshold_returns_none(self, base_listing, base_analysis):
        policy = SellerFeedbackPolicy(min_feedback_percentage=85.0)
        assert policy.apply(base_listing, base_analysis) is None

    def test_below_threshold_returns_skip(self, base_analysis):
        listing = Listing(
            id="v1|123|0",
            title="Manteau mauvais vendeur",
            price=Money(value=20.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=80.0,
            accepts_returns=True,
        )
        policy = SellerFeedbackPolicy(min_feedback_percentage=85.0)
        assert policy.apply(listing, base_analysis) == RecommandationLevel.SKIP

    def test_exactly_at_threshold_returns_skip(self, base_analysis):
        listing = Listing(
            id="v1|123|0",
            title="Manteau vendeur seuil",
            price=Money(value=20.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.GOOD,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=85.0,
            accepts_returns=True,
        )
        policy = SellerFeedbackPolicy(min_feedback_percentage=85.0)
        assert policy.apply(listing, base_analysis) == RecommandationLevel.SKIP


class TestWarmthPolicy:
    def test_above_threshold_returns_none(self, base_listing, base_analysis):
        policy = WarmthPolicy(min_warmth_score=1.0)
        assert policy.apply(base_listing, base_analysis) is None

    def test_below_threshold_returns_skip(self, base_listing):
        cold_analysis = LLMAnalysis(listing_id="v1|123|0", warmth_score=0.5)
        policy = WarmthPolicy(min_warmth_score=1.0)
        assert policy.apply(base_listing, cold_analysis) == RecommandationLevel.SKIP

    def test_exactly_at_threshold_returns_skip(self, base_listing):
        analysis = LLMAnalysis(listing_id="v1|123|0", warmth_score=1.0)
        policy = WarmthPolicy(min_warmth_score=1.0)
        assert policy.apply(base_listing, analysis) == RecommandationLevel.SKIP
