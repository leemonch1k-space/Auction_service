import asyncio
from src.config.celery_app import celery_instance
from src.database.celery_session import task_db_session
from src.services.auction import send_lot_to_winner

# Celery tasks for auction


async def _run_auction_closure(auction_id: int) -> None:
    """Support method for celery task."""
    async with task_db_session() as db:
        await send_lot_to_winner(auction_id=auction_id, db=db)


@celery_instance.task(name="send_lot_item_to_user_task")
def send_lot_item_to_user_task(auction_id: int) -> None:
    """
    Celery-task to send a lot to winner.
    """
    asyncio.run(_run_auction_closure(auction_id))
