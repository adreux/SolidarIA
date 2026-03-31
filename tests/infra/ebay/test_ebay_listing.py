import json

import pytest

from src.infra.ebay.ebay_listing import EbayItemDetail, EbayItemSummary


@pytest.fixture
def search_data():
    with open("data/json_response/search_response.json") as f:
        data = json.load(f)
    return data["itemSummaries"][0]


@pytest.fixture
def detail_data():
    with open("data/json_response/search_item_ref_response.json") as f:
        return json.load(f)


def test_summary_mapper(search_data):
    item = EbayItemSummary.from_ebay_json(search_data)
    assert item.item_id is not None
    assert item.price.value > 0
    assert item.condition.conditionId is not None


def test_detail_mapper(detail_data):
    item = EbayItemDetail.from_ebay_json(detail_data)
    assert item.item_id is not None
    assert item.seller is not None
    assert item.brand is not None
