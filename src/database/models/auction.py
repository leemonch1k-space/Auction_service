from datetime import datetime
from decimal import Decimal
from typing import List, TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    Text,
    Enum,
    Numeric,
    CheckConstraint,
    DateTime,
    func,
    Boolean,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.database import Base
from src.enums import AuctionStageEnum
from src.utils import get_24h_from_now

if TYPE_CHECKING:
    from src.database.models.user import UserModel


class CollectionModel(Base):
    """Table model for lots storage."""

    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )

    lots: Mapped[List["LotModel"]] = relationship(
        "LotModel",
        back_populates="collection",
        cascade="all, delete-orphan",
    )
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="collection"
    )


class LotModel(Base):
    """Table model for lot."""

    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(
        Text, nullable=False, default="No description provided"
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        CheckConstraint("price > 0", name="check_lot_price_positive"),
        nullable=False,
        default=0.00,
    )
    is_on_auction: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id"), nullable=False
    )

    collection: Mapped["CollectionModel"] = relationship(
        "CollectionModel", back_populates="lots"
    )


class AuctionModel(Base):
    """Table model for auction."""

    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    status: Mapped[AuctionStageEnum] = mapped_column(
        Enum(AuctionStageEnum),
        nullable=False,
        default=AuctionStageEnum.RUNNING
    )
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    lot_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        CheckConstraint("lot_price > 0", name="check_auction_price_positive"),
        nullable=False,
    )
    current_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        CheckConstraint(
            "current_price > 0", name="check_auction_current_price_positive"
        ),
        nullable=False,
    )
    lot_id: Mapped[int] = mapped_column(ForeignKey("lots.id"), nullable=False)
    bid_step: Mapped[Decimal] = mapped_column(
        Numeric(precision=7, scale=2),
        CheckConstraint("bid_step > 0", name="check_bid_step_positive"),
        nullable=False,
    )
    top_bidder_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_24h_from_now, nullable=False
    )

    creator: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[creator_id]
    )
    top_bidder: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[top_bidder_id]
    )
    lot: Mapped["LotModel"] = relationship()
