import logging

import dotenv
from pydantic import BaseModel, ConfigDict, Field

from src.logger import setup_logging

setup_logging()
dotenv.load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Price(BaseModel):
    value: float
    currency: str


class Condition(BaseModel):
    """
    Condition of the item.
    Check here for more details https://developer.ebay.com/api-docs/sell/static/metadata/condition-id-values.html
    """

    conditionId: str
    condition: str
    conditionDescription: str | None = None


class Seller(BaseModel):
    username: str
    feedbackScore: int
    feedbackPercentage: float
    sellerAccountType: str


class Delivery(BaseModel):
    shippingCost: Price
    shippingService: str
    shippingCostType: str
    shippingTimeMin: int
    shippingTimeMax: int


class EbayItemSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    item_id: str = Field(alias="itemId")
    title: str
    price: Price
    condition: Condition
    image_url: str = Field(alias="imageUrl")
    item_href: str = Field(alias="itemHref", default="")
    item_web_url: str = Field(alias="itemWebUrl")
    buying_options: list[str] = Field(alias="buyingOptions")
    shipping_cost: float

    @classmethod
    def from_ebay_json(cls, data: dict) -> "EbayItemSummary":
        return cls(
            item_id=data["itemId"],
            title=data["title"],
            price=Price(
                value=data["price"]["value"], currency=data["price"]["currency"]
            ),
            condition=Condition(
                conditionId=data["conditionId"],
                condition=data["condition"],
                conditionDescription=data.get("conditionDescription"),
            ),
            image_url=data["image"]["imageUrl"],
            item_href=data.get("itemHref", ""),
            item_web_url=data["itemWebUrl"],
            buying_options=data["buyingOptions"],
            shipping_cost=float(data["shippingOptions"][0]["shippingCost"]["value"]),
        )


class EbayItemDetail(EbayItemSummary):
    short_description: str | None = Field(default=None, alias="shortDescription")
    description: str | None = Field(default=None)
    brand: str | None = Field(default=None)
    size: str | None = Field(default=None)
    color: str | None = Field(default=None)
    condition_description: str | None = Field(
        default=None, alias="conditionDescription"
    )
    return_terms: bool = Field(default=False, alias="returnTerms")
    seller: Seller | None = Field(default=None)
    additional_images: list[str] = Field(default_factory=list, alias="additionalImages")
    estimated_available_quantity: int = Field(default=0)

    @classmethod
    def from_ebay_json(cls, data: dict) -> "EbayItemDetail":
        base = EbayItemSummary.from_ebay_json(data).model_dump()
        return cls(
            **base,
            short_description=data.get("shortDescription"),
            description=data.get("description"),
            brand=data.get("brand"),
            size=data.get("size"),
            color=data.get("color"),
            condition_description=data.get("conditionDescription"),
            return_terms=data.get("returnTerms", {}).get("returnsAccepted", False),
            seller=Seller(**data["seller"]),
            additional_images=[
                img["imageUrl"] for img in data.get("additionalImages", [])
            ],
            estimated_available_quantity=data.get("estimatedAvailabilities", [{}])[
                0
            ].get("estimatedAvailableQuantity", 0),
        )
