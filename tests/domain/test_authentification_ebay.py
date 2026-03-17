from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.domain.authentification_ebay import EbayApi


@pytest.fixture
def ebay_api(monkeypatch):
    monkeypatch.setenv("app_id", "fake_app_id")
    monkeypatch.setenv("dev_id", "fake_dev_id")
    monkeypatch.setenv("client_secret", "fake_secret")
    return EbayApi()


def test_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv("app_id", raising=False)
    monkeypatch.delenv("dev_id", raising=False)
    monkeypatch.delenv("client_secret", raising=False)
    with pytest.raises(ValueError):
        EbayApi()


def test_token_is_refreshed(ebay_api):
    with patch("src.domain.authentification_ebay.requests.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"access_token": "fake_token", "expires_in": 7200},
        )
        token = ebay_api.access_token
        assert token == "fake_token"
        mock_post.assert_called_once()


def test_token_not_refreshed_if_valid(ebay_api):
    ebay_api._access_token = "existing_token"
    ebay_api._expiration_time = datetime.now() + timedelta(hours=1)
    with patch("src.domain.authentification_ebay.requests.post") as mock_post:
        token = ebay_api.access_token
        assert token == "existing_token"
        mock_post.assert_not_called()


def test_search_item(ebay_api):
    ebay_api._access_token = "fake_token"
    ebay_api._expiration_time = datetime.now() + timedelta(hours=1)
    with patch("src.domain.authentification_ebay.requests.get") as mock_get:
        mock_get.return_value = MagicMock(
            status_code=200, json=lambda: {"itemSummaries": []}
        )
        result = ebay_api.search_item("manteau")
        assert "itemSummaries" in result
        mock_get.assert_called_once()
