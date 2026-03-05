import logging
import os
from dataclasses import dataclass

import dotenv

from src.logger import setup_logging

setup_logging()
dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class EbayApi:
    def __post_init__(self):
        self.app_id = os.getenv("app_id")
        self.dev_id = os.getenv("dev_id")
        self.client_secret = os.getenv("client_secret")


def main():
    ebayapi = EbayApi()
    logger.info(f"App ID: {len(ebayapi.app_id)}")


if __name__ == "__main__":
    main()
