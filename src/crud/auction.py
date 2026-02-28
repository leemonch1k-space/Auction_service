import datetime
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    UserModel,
    CollectionModel,
    LotModel,
    AuctionModel,
)
from src.enums import (
    AuctionStageEnum,
)
from src.exceptions import (
    CollectionNotExist,
    LotItemNotExists,
    LotItemAlreadyOnSaleError,
    AuctionAlreadyEnded,
    SelfBetNotAllowed,
    InsufficientBalance, BidBelowMinimum
)
from src.schemas import (
    AuctionResponseSchema,
    CreateAuctionSchema,
    LotCreateSchema,
    LotResponseSchema,
    CollectionResponseSchema,
    AuctionListSchema,
    MakeBetSchema, MakeBetResponseSchema,
)
from src.config.dependencies import get_db, get_authenticated_user
from src.tasks.auction_tasks import send_lot_item_to_user_task


async def get_user_collection(
        db: Annotated[AsyncSession, Depends(get_db)],
        authenticated_user_data: Annotated[UserModel, Depends(get_authenticated_user)],
) -> CollectionResponseSchema:
    query = (
        select(CollectionModel)
        .where(CollectionModel.owner_id == authenticated_user_data.id)
        .options(selectinload(CollectionModel.lots))
    )
    db_collection = await db.scalar(query)


    if not db_collection:
        raise CollectionNotExist("Collection not exists!")

    return db_collection


async def create_new_lot_item(
        db: Annotated[AsyncSession, Depends(get_db)],
        authenticated_user_data: Annotated[UserModel, Depends(get_authenticated_user)],
        lot_data: LotCreateSchema,
) -> LotResponseSchema:
    new_lot = LotModel(
        **lot_data.model_dump(),
        collection_id=authenticated_user_data.collection.id
    )

    try:
        db.add(new_lot)
        await db.commit()
        await db.refresh(new_lot)
    except IntegrityError:
        await db.rollback()
        raise

    return new_lot


async def create_new_auction(
        db: Annotated[AsyncSession, Depends(get_db)],
        authenticated_user_data: Annotated[UserModel, Depends(get_authenticated_user)],
        auction_data: CreateAuctionSchema,
) -> AuctionResponseSchema:
    query = (
        select(LotModel)
        .join(CollectionModel)
        .where(
            and_(
                LotModel.id == auction_data.lot_id,
                CollectionModel.owner_id == authenticated_user_data.id
            )
        )
    )
    lot = await db.scalar(query)

    if not lot:
        raise LotItemNotExists(
            "Lot not found or you do not own this lot"
        )

    if lot.is_on_auction:
        raise LotItemAlreadyOnSaleError(
            "This lot is already on auction"
        )

    new_auction = AuctionModel(
        status=auction_data.status,
        bid_step=auction_data.bid_step,
        lot_id=lot.id,
        creator_id=authenticated_user_data.id,
        lot_price=lot.price,
        current_price=lot.price,
    )

    lot.is_on_auction = True

    try:
        db.add(new_auction)
        await db.commit()
        await db.refresh(new_auction)

        new_auction.lot = lot
    except IntegrityError:
        await db.rollback()
        raise

    execution_time = new_auction.end_at + datetime.timedelta(minutes=1)
    send_lot_item_to_user_task.apply_async(
        args=[new_auction.id],
        eta=execution_time
    )
    return new_auction


async def get_auctions(
        db: Annotated[AsyncSession, Depends(get_db)],
        authenticated_user_data: Annotated[UserModel, Depends(get_authenticated_user)],
) -> AuctionListSchema:
    query = (
        select(AuctionModel)
        .where(AuctionModel.status == AuctionStageEnum.RUNNING)
        .options(selectinload(AuctionModel.lot))
    )
    db_auctions = await db.scalars(query)

    return AuctionListSchema(auctions=db_auctions.all())


async def make_bet(
        db: Annotated[AsyncSession, Depends(get_db)],
        authenticated_user_data: UserModel,
        lot_id: int,
        bet_data: MakeBetSchema
) -> MakeBetResponseSchema:
    query = (
        select(AuctionModel)
        .where(AuctionModel.lot_id == lot_id)
        .with_for_update()
    )
    auction_data = await db.scalar(query)

    if not auction_data:
        lot = await db.get(LotModel, lot_id)
        if not lot:
            raise LotItemNotExists("Lot does not exist")
        raise AuctionAlreadyEnded("Auction is not active")

    if auction_data.status != AuctionStageEnum.RUNNING:
        raise AuctionAlreadyEnded("Auction already ended")

    if auction_data.creator_id == authenticated_user_data.id:
        raise SelfBetNotAllowed("You can't place a bet on your own lot")

    if authenticated_user_data.balance < bet_data.bet:
        raise InsufficientBalance("Insufficient funds")

    min_required_bid = auction_data.current_price + auction_data.bid_step

    if bet_data.bet < min_required_bid:
        raise BidBelowMinimum(f"Bid must be at least {min_required_bid}")

    auction_data.current_price = bet_data.bet
    auction_data.top_bidder_id = authenticated_user_data.id

    await db.commit()
    await db.refresh(auction_data)

    return MakeBetResponseSchema(
        lot_id=lot_id,
        bet=auction_data.current_price,
        user_id=authenticated_user_data.id
    )
