from typing import Annotated

from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.crud import (
    get_user_collection,
    create_new_lot_item,
    create_new_auction,
    get_auctions,
)
from src.config.dependencies import get_db, get_authenticated_user
from src.crud.auction import make_bet
from src.database.models import UserModel
from src.exceptions import (
    BaseUserException,
    BaseCollectionException,
    BaseLotException,
    BaseAuctionException,
)
from src.schemas import (
    AuctionResponseSchema,
    CreateAuctionSchema,
    LotCreateSchema,
    LotResponseSchema,
    CollectionResponseSchema,
    AuctionListSchema,
    MakeBetSchema,
    MakeBetResponseSchema,
)
from src.websockets import manager

auction_router = APIRouter(prefix="/auction", tags=["Auction"])


@auction_router.get(
    "/collection/",
    status_code=status.HTTP_200_OK,
    response_model=CollectionResponseSchema,
    summary="Get user lot's storage",
    description="return authenticated user collection with lots",
)
async def get_collection(
    db: Annotated[AsyncSession, Depends(get_db)],
    authenticated_user_data: Annotated[
        UserModel, Depends(get_authenticated_user)
    ],  # noqa
) -> CollectionResponseSchema:
    """Controller for getting user's storage."""
    try:
        return await get_user_collection(
            db=db,
            authenticated_user_data=authenticated_user_data,
        )
    except BaseCollectionException as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@auction_router.post(
    "/collection/lot/",
    status_code=status.HTTP_201_CREATED,
    response_model=LotResponseSchema,
    summary="Create new lot item",
    description="Create new lot item and save it to user's collection",
)
async def add_new_lot_item(
    db: Annotated[AsyncSession, Depends(get_db)],
    authenticated_user_data: Annotated[
        UserModel, Depends(get_authenticated_user)
    ],  # noqa
    lot_data: LotCreateSchema,
) -> LotResponseSchema:
    """Controller for creating new lot item."""
    try:
        return await create_new_lot_item(
            db=db,
            authenticated_user_data=authenticated_user_data,
            lot_data=lot_data,
        )
    except IntegrityError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@auction_router.post(
    "/lots/",
    status_code=status.HTTP_201_CREATED,
    response_model=AuctionResponseSchema,
    summary="Begin new auction",
    description="Create new auction instance to start new auction",
)
async def begin_auction(
    db: Annotated[AsyncSession, Depends(get_db)],
    authenticated_user_data: Annotated[
        UserModel, Depends(get_authenticated_user)
    ],  # noqa
    auction_data: CreateAuctionSchema,
) -> AuctionResponseSchema:
    """Controller for creating new auction."""
    try:
        return await create_new_auction(
            db=db,
            authenticated_user_data=authenticated_user_data,
            auction_data=auction_data,
        )
    except (BaseLotException, IntegrityError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@auction_router.get(
    "/lots/",
    status_code=status.HTTP_200_OK,
    response_model=AuctionListSchema,
    summary="Get active auctions",
    description="return list of running auction",
)
async def get_running_auctions(
    db: Annotated[AsyncSession, Depends(get_db)],
    authenticated_user_data: Annotated[
        UserModel, Depends(get_authenticated_user)
    ],  # noqa
) -> AuctionListSchema:
    try:
        return await get_auctions(
            db=db,
            authenticated_user_data=authenticated_user_data,
        )
    except BaseCollectionException as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@auction_router.post(
    "/lots/{lot_id}/bids/",
    status_code=status.HTTP_200_OK,
    response_model=MakeBetResponseSchema,
    summary="Place a bet",
    description="Place a bet on auction lot",
)
async def place_bet(
    db: Annotated[AsyncSession, Depends(get_db)],
    authenticated_user_data: Annotated[
        UserModel, Depends(get_authenticated_user)
    ],  # noqa
    lot_id: int,
    bet_data: MakeBetSchema,
) -> MakeBetResponseSchema:
    """Controller for place bet on lot."""
    try:
        result = await make_bet(
            db=db,
            authenticated_user_data=authenticated_user_data,
            lot_id=lot_id,
            bet_data=bet_data,
        )
        notification = {
            "type": "new_bid",
            "lot_id": str(lot_id),
            "amount": float(bet_data.bet),
            "bidder": str(authenticated_user_data.login),
        }
        await manager.broadcast(lot_id, notification)

        return result
    except (
        BaseUserException,
        BaseAuctionException,
        BaseLotException,
        IntegrityError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


@auction_router.websocket("/ws/lots/{lot_id}/")
async def connect_to_auction(websocket: WebSocket, lot_id: int):
    """
    Public websocket.
    Any client can connect to retrieve updates about auction.
    """
    await manager.connect(websocket, lot_id)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket, lot_id)
