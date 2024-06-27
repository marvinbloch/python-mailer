from typing import List

from ..models.models import Email
from ..services.crud import get_all_emails, update_email_reachable_status
from ..utils.validatorEmail import check_reachable
from ..config.logging_setup import logger


async def update_reachable_emails_task(db):
    try:
        emails: List[Email] = await get_all_emails(db)
        count = 0
        async with db.begin():
            for emailDB in emails:
                reachable = await check_reachable(emailDB.email)
                if emailDB.reachable != reachable:
                    await update_email_reachable_status(emailDB, reachable)
                    count += 1
                    logger.info(f"Successfully updated reachability status for {emailDB.email}")
        logger.info(f"Successfully updated reachability status for {count} emails")
        logger.info("Updating Task ended successfull")
        return {"message": f"Successfully updated reachability status for {count} emails", "error": False}
    except Exception as e:
        logger.error(f"Updating Task failed: {e}")
        return {"message": "Failed to update reachable emails", "error": True}