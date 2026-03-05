import base64
import logging
import os
from datetime import datetime, timedelta

import dotenv
import requests

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
    def access_token(self):
        if self._access_token is None or datetime.now() >= self._expiration_time:
            self._access_token = self._refresh_access_token()
            self._expiration_time = datetime.now() + timedelta(seconds=7200)
        return self._access_token

    def _refresh_access_token(self):
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
            self._access_token = request_response.json().get("access_token")
            logger.info("Access token obtained successfully.")
        else:
            logger.error(
                f"Failed to obtain access token: {request_response.status_code} - {request_response.text}"
            )
            raise Exception(
                f"Failed to obtain access token: {request_response.status_code} - {request_response.text}"
            )
        return self._access_token
        # return request_response.json()


def main():
    ebayapi = EbayApi()
    print(f"request_response: {ebayapi.access_token}")


if __name__ == "__main__":
    main()
