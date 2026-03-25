import base64
import json
import logging
import os
from datetime import datetime, timedelta

import dotenv
import requests

from src.domain.authentification_ebay import EbayItemDetail, EbayItemSummary
from src.logger import setup_logging

setup_logging()
dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EbayApi:
    def __init__(self):
        self.app_id = os.getenv("app_id")
        self.dev_id = os.getenv("dev_id")
        self.client_secret = os.getenv("client_secret")
        if not self.app_id or not self.dev_id or not self.client_secret:
            logger.error("Missing eBay API credentials in environment variables.")
            raise ValueError("Missing eBay API credentials in environment variables.")
        logger.info("eBay API credentials loaded successfully.")
        self._access_token = None
        self._expiration_time = None

    @property
    def access_token(self) -> str:
        if self._access_token is None or datetime.now() >= self._expiration_time:
            self._access_token = self._refresh_access_token()
        return self._access_token

    def _refresh_access_token(self) -> str:
        url_token_endpoint = "https://api.ebay.com/identity/v1/oauth2/token"

        credentials = f"{self.app_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}",
        }

        body = {
            "grant_type": "client_credentials",
            "scope": "https://api.ebay.com/oauth/api_scope",
        }

        try:
            request_response = requests.post(
                url_token_endpoint, headers=headers, data=body
            )
        except Exception as e:
            logger.error(f"Error during token request: {e}")
            raise

        if request_response.status_code == 200:
            data = request_response.json()
            self._access_token = request_response.json().get("access_token")
            self._expiration_time = datetime.now() + timedelta(
                seconds=data.get("expires_in", 7200)
            )
            logger.info("Access token obtained successfully.")
        else:
            logger.error(
                f"Failed to obtain access token: {request_response.status_code} - {request_response.text}"
            )
            raise Exception(
                f"Failed to obtain access token: {request_response.status_code} - {request_response.text}"
            )
        return self._access_token

    def _get(self, url: str, params: dict = None) -> dict:
        # uniquement la requête HTTP
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_FR",
        }
        try:
            response = requests.get(url, headers=headers, params=params)
        except Exception as e:
            logger.error(f"Error during request: {e}")
            raise
        if response.status_code == 200:
            logger.info(f"Request successful: {response.status_code} - {response.text}")
            return response.json()
        else:
            logger.error(f"Request failed: {response.status_code} - {response.text}")
            raise Exception(f"Request failed: {response.status_code} - {response.text}")

    def search_item(self, query: str) -> list[EbayItemSummary]:
        data = self._get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            params={"q": query},
        )
        return [EbayItemSummary.from_ebay_json(item) for item in data["itemSummaries"]]

    def search_item_ref(self, url: str) -> EbayItemDetail:
        data = self._get(url)
        return EbayItemDetail.from_ebay_json(data)


def main():
    ebayapi = EbayApi()
    ebayitemdetail = ebayapi.search_item_ref(
        "https://api.ebay.com/buy/browse/v1/item/v1%7C358311088969%7C626586956773"
    )
    #    path_item = "data/json_response/search_response.json"
    path_item_ref = "data/json_response/search_item_ref_response.json"
    with open(path_item_ref, "w") as f:
        json.dump(ebayitemdetail.model_dump(), f, indent=4)


if __name__ == "__main__":
    main()
