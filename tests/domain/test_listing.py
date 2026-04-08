from dataclasses import FrozenInstanceError

import pytest

from src.domain.listing import ConditionGrade, Listing, Money


@pytest.fixture
def sample_listing():
    return Listing(
        id="v1|123|0",
        title="Manteau d'hiver",
        price=Money(value=45.0, currency="EUR"),
        shipping_cost=5.0,
        condition=ConditionGrade.VERY_GOOD,
        condition_description="Quelques légères traces d'usure",
        description="<p>Manteau chaud en laine</p>",
        image_urls=["https://example.com/img1.jpg"],
        seller_feedback_percentage=98.5,
        accepts_returns=True,
    )


class TestConditionGrade:
    def test_from_ebay_id_new(self):
        assert ConditionGrade.from_ebay_id("1000") == ConditionGrade.NEW

    def test_from_ebay_id_very_good(self):
        assert ConditionGrade.from_ebay_id("3000") == ConditionGrade.VERY_GOOD

    def test_from_ebay_id_good(self):
        assert ConditionGrade.from_ebay_id("5000") == ConditionGrade.GOOD

    def test_from_ebay_id_unknown_fallback(self):
        assert ConditionGrade.from_ebay_id("9999") == ConditionGrade.UNKNOWN

    def test_from_ebay_id_empty_string(self):
        assert ConditionGrade.from_ebay_id("") == ConditionGrade.UNKNOWN


class TestListing:
    def test_instantiation(self, sample_listing):
        assert sample_listing.id == "v1|123|0"
        assert sample_listing.price.value == 45.0
        assert sample_listing.condition == ConditionGrade.VERY_GOOD

    def test_frozen_price(self, sample_listing):
        with pytest.raises(FrozenInstanceError):
            sample_listing.price = Money(value=99.0, currency="EUR")

    def test_frozen_condition(self, sample_listing):
        with pytest.raises(FrozenInstanceError):
            sample_listing.condition = ConditionGrade.NEW

    def test_money_total_eur_returns_value(self):
        money = Money(value=42.0, currency="EUR")
        assert money.total_eur == 42.0

    def test_money_total_eur_raises_for_non_eur(self):
        money = Money(value=42.0, currency="USD")
        with pytest.raises(ValueError, match="not supported"):
            _ = money.total_eur

    def test_optional_fields_can_be_none(self):
        listing = Listing(
            id="v1|456|0",
            title="Manteau basique",
            price=Money(value=20.0, currency="EUR"),
            shipping_cost=0.0,
            condition=ConditionGrade.UNKNOWN,
            condition_description=None,
            description=None,
            image_urls=[],
            seller_feedback_percentage=0.0,
            accepts_returns=False,
        )
        assert listing.condition_description is None
        assert listing.description is None
        assert listing.image_urls == []
