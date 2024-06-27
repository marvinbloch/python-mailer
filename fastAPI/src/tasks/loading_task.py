from ..config.config import EMAIL_FILE_PATH
from ..services.crud import create_email, get_email_by_email
from ..utils.readFiles import read_email_from_files
from ..utils.validatorEmail import initial_email
from ..config.logging_setup import logger
from ..models.models import Email


async def load_emails_to_database_task(db):
    try:
        emails = await read_email_from_files(EMAIL_FILE_PATH)
        
        added_emails = []
        async with db.begin():
            for email in emails:
                if not await get_email_by_email(db, email):
                    logger.info(f"Loading email {email} into the database")
                    email_entry: Email = await initial_email(email)
                    added_emails.append(await create_email(db, email_entry))
                else:
                    logger.info(f"Email {email} already exists in the database")
        
        
        logger.info(f"Successfully loaded {len(added_emails)} emails into the database")
        logger.info("Loading Task ended successfull")
        return {"message": f"Successfully loaded {len(added_emails)} emails into the database", "error": False}
    except Exception as e:
        logger.error(f"Loading Task failed: {e}")
        return {"message": "Failed to load emails", "error": True}