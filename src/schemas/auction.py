from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.enums import AuctionStageEnum


class LotCreateSchema(BaseModel):
    """Schema for creating lot item instance."""
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
    """Base lot schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class LotResponseSchema(LotSchema):
    """Schema for lot response."""
    price: Decimal
    is_on_auction: bool


class CollectionResponseSchema(BaseModel):
    """Schema for collection response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    lots: list[LotResponseSchema]


class CreateAuctionSchema(BaseModel):
    """Schema for creating auction instance."""
    status: AuctionStageEnum = AuctionStageEnum.RUNNING
    bid_step: Decimal = Field(gt=0, max_digits=7, decimal_places=2)
    lot_id: int


class AuctionResponseSchema(BaseModel):
    """Schema for auction response."""
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
    """Schema for auction item."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: AuctionStageEnum
    lot: LotSchema
    current_price: Decimal
    bid_step: Decimal


class AuctionListSchema(BaseModel):
    """Schema for auction instance list response."""
    auctions: list[AuctionItemSchema]


class MakeBetSchema(BaseModel):
    """Schema for placing bet."""
    bet: Decimal


class MakeBetResponseSchema(BaseModel):
    """Schema for bet response."""
    lot_id: int
    bet: Decimal
    user_id: int
