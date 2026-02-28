from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.enums import AuctionStageEnum


class LotCreateSchema(BaseModel):
    name: str
    description: str
    price: Decimal = Field(gt=0, decimal_places=2)

    @field_validator("description", mode="before")
    @classmethod
    def set_default_description(cls, v):
        if not v or not v.strip():
            return "No description provided"
        return v


class LotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class LotResponseSchema(LotSchema):
    price: Decimal
    is_on_auction: bool


class CollectionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lots: list[LotResponseSchema]


class CreateAuctionSchema(BaseModel):
    status: AuctionStageEnum = AuctionStageEnum.RUNNING
    bid_step: Decimal = Field(gt=0, max_digits=7, decimal_places=2)
    lot_id: int


class AuctionResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: AuctionStageEnum
    creator_id: int
    lot_price: Decimal
    lot: LotSchema
    current_price: Decimal
    top_bidder_id: Optional[int] = None
    bid_step: Decimal


class AuctionItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: AuctionStageEnum
    lot: LotSchema
    current_price: Decimal
    bid_step: Decimal


class AuctionListSchema(BaseModel):
    auctions: list[AuctionItemSchema]


class MakeBetSchema(BaseModel):
    bet: Decimal


class MakeBetResponseSchema(BaseModel):
    lot_id: int
    bet: Decimal
    user_id: int
