from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.models import ConnectionLog, Email, EmailHistory
from ..utils.tracking_id import generate_tracking_id
from ..config.logging_setup import logger

async def get_all_emails(db: AsyncSession) -> List[Email]:
    result = await db.execute(select(Email))
    return result.scalars().all()

async def get_email_by_email(db: AsyncSession, email: str) -> Email:
    result = await db.execute(select(Email).where(Email.email == email))
    return result.scalars().first()

async def get_email_by_id(db: AsyncSession, email_id: int) -> Email:
    return await db.get(Email, email_id)

async def get_all_sendable_emails(db: AsyncSession) -> List[Email]:
    result = await db.execute(
        select(Email).where(
            Email.active == True,
            Email.valid == True,
            Email.reachable == True
        )
    )
    return result.scalars().all()

async def get_history_by_tracking_id(db: AsyncSession, tracking_id: str) -> EmailHistory:
    result = await db.execute(select(EmailHistory).where(EmailHistory.tracking_id == tracking_id))
    return result.scalars().first()

async def get_histories_by_email_id(db: AsyncSession, email_id: int):
    result = await db.execute(select(EmailHistory).where(EmailHistory.email_id == email_id))
    return result.scalars().all()

async def generate_unique_tracking_id(db: AsyncSession) -> str:
    while True:
        tracking_id = generate_tracking_id()
        history: EmailHistory = None
        try:
            history = await get_history_by_tracking_id(db, tracking_id)
        except Exception as e:
            logger.error(f"Error while checking tracking ID: {e}")
        finally:
            if history is None:
                return tracking_id


async def create_email(db: AsyncSession, email: Email) -> Email:
    db.add(email)
    await db.flush()
    await db.refresh(email)
    return email
    

async def create_email_history(db: AsyncSession, email_id: int, tracking_id: str, redirect_url: str, success: bool) -> EmailHistory:
    db_email_history: EmailHistory = EmailHistory(
        email_id=email_id,
        tracking_id=tracking_id,
        redirect_url=redirect_url,
        success=success
    )
    db.add(db_email_history)
    await db.flush()
    await db.refresh(db_email_history)
    return db_email_history

async def update_email_reachable_status(db: AsyncSession, email_id: int, reachable: bool):
    email: Email = await get_email_by_id(db, email_id)
    if (email):
        email.reachable = reachable
        db.add(email)
        await db.flush()
        await db.refresh(email)
    return email

async def update_email_reachable_status_object(db: AsyncSession, email: Email, reachable: bool):
    email.reachable = reachable
    await db.commit()
    await db.refresh(email)

async def update_history_clicks(db: AsyncSession, history: EmailHistory) -> EmailHistory:
    history.click_count += 1
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def create_connection_log(
    db: AsyncSession, tracking_id: str, origin: str, user_agent: str, referer: str,
    path: str, query_params: str, status_code: int, response_time: int, message: str
) -> ConnectionLog:
    log_entry = ConnectionLog(
        tracking_id=tracking_id,
        origin=origin,
        user_agent=user_agent,
        referer=referer,
        path=path,
        query_params=query_params,
        status_code=status_code,
        response_time=response_time,
        message=message
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry






