import time
from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ..config.logging_setup import logger
from ..config.config import REDIRECT_URL
from ..services.crud import get_history_by_tracking_id, update_history_clicks, get_email_by_id, create_connection_log
from ..config.database import get_task_db
from ..models.models import EmailHistory


async def track_click_func(tracking_id: str, request: Request, db: AsyncSession):
    redirect_url = REDIRECT_URL
    origin = request.client.host
    user_agent = request.headers.get('user-agent', 'unknown')
    referer = request.headers.get('referer', 'unknown')
    path = request.url.path
    query_params = str(request.query_params)
    start_time = time.time()

    try:
        history: EmailHistory = await get_history_by_tracking_id(db, tracking_id)
        if history:
            updated_history: EmailHistory = await update_history_clicks(db, history)
            emailDB = await get_email_by_id(db, history.email_id)
            logger.info(f"Email {emailDB.email} clicked, total clicks: {updated_history.click_count}")
            redirect_url = history.redirect_url
            message = "Click tracked successfully"
            status_code = 200
        else:
            logger.warning(f"Email not found for tracking_id: {tracking_id}")
            message = "Email not found"
            status_code = 404
    except Exception as e:
        logger.error(f"Error tracking click for key {tracking_id}: {e}")
        message = f"Error: {e}"
        status_code = 500
    finally:
        response_time = int((time.time() - start_time) * 1000)
        await create_connection_log(
            db, tracking_id, origin, user_agent, referer, path, query_params, status_code, response_time, message
        )
        return RedirectResponse(url=redirect_url)
