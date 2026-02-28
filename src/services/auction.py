from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from celery.utils.log import get_task_logger

from src.database.models import (
    AuctionModel,
    UserModel,
    LotModel,
)
from src.enums import AuctionStageEnum
from src.websockets import manager

logger = get_task_logger(__name__)


async def send_lot_to_winner(
        auction_id: int,
        db: AsyncSession
) -> None:
    auction_data = await db.get(AuctionModel, auction_id)
    if not auction_data:
        print(f"Auction {auction_id} not found.")
        return

    stmt_winner = (
        select(UserModel)
        .where(UserModel.id == auction_data.top_bidder_id)
        .options(selectinload(UserModel.collection))
    )
    winner = await db.scalar(stmt_winner)

    owner = await db.get(UserModel, auction_data.creator_id)
    lot = await db.get(LotModel, auction_data.lot_id)

    if not winner or not owner or not lot:
        logger.error("User or Lot not found.")
        return

    auction_data.status = AuctionStageEnum.ENDED
    winner.balance -= auction_data.current_price
    owner.balance += auction_data.current_price

    if winner.collection:
        lot.collection_id = winner.collection.id
    else:
        logger.error(f"User {winner.login} has no collection!")

    # additional notification for auction broadcast
    notification = {
        "type": "info",
        "winner": str(winner.login),
        "message": "The auction has ended, praise the winner!"
    }
    await manager.broadcast(auction_data.lot_id, notification)

    # as another option could be removed by another task
    await db.delete(auction_data)
    logger.info(f"Auction {auction_id} instance deleted.")


    await db.commit()
    logger.info(f"Auction {auction_id} processed successfully.")
