from typing import List
import aiosmtplib
import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

from ..config.database import TaskSessionLocal

from ..services.crud import create_email_history, generate_unique_tracking_id, update_email_reachable_status
from ..models.models import Email
from ..utils.readFiles import load_template, load_subject, load_redirect_url
from ..utils.validatorEmail import check_reachable
from ..config.config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD, SERVER_URL, EMAIL_TEMPLATE_PATH, SUBJECT_FILE_PATH, REDIRECT_URL_FILE_PATH

from ..config.logging_setup import logger

async def send_emails_task(db, recipients: List[Email]):
    try:
        if recipients:
            tasks = [send_single_email(db, recipient) for recipient in recipients]
            await asyncio.gather(*tasks)
            logger.info("Sending Task ended successfull")
        else:
            logger.info("Sending Task stopped: No Emails to send")
        return {"message": "Emails sending done.", "error": False}
    except Exception as e:
        logger.error(f"Sending Task failed: {e}")
        return {"message": "Failed to send emails", "error": True}
    
async def send_single_email(db, recipient: Email):
    try:
        tracking_id = await generate_unique_tracking_id(db)

        template_content = await load_template(EMAIL_TEMPLATE_PATH)

        subject = await load_subject(SUBJECT_FILE_PATH)

        redirect_url = await load_redirect_url(REDIRECT_URL_FILE_PATH)

        template = Template(template_content)

        body = template.render(
            tracking_id=tracking_id,
            domain=SERVER_URL
        )

        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_SENDER
        msg["To"] = recipient.email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, 'html'))
        
        if (await check_reachable(recipient.email)):
            success, error = await send_mail(recipient.email, msg)
            async with TaskSessionLocal() as task_db:
                async with task_db.begin():
                    try:
                        updatedEmail = await update_email_reachable_status(task_db, recipient.id, success)
                        logger.info(f"Updated reachable status for {updatedEmail.email} is now {updatedEmail.reachable}!")
                    except Exception as e:
                        logger.error(f"Updating reachable status for {recipient.email} in database was not possible: {e}")
                    
                    try:
                        await create_email_history(
                            task_db, 
                            email_id=recipient.id, 
                            tracking_id=tracking_id, 
                            redirect_url=redirect_url, 
                            success=success
                        )
                        logger.info(f"Created email history for {recipient.email} successfully!")
                    except Exception as e:
                        logger.error(f"Creating email history for {recipient.email} failed: {e}")
                    task_db.commit()
                if success:
                    logger.info(f"Sending Email to {recipient.email} was successfull!")
                else:
                    raise Exception(error)
        else:
            raise Exception("Email is not Reachable")
    except Exception as e:
        logger.error(f"Sending Email to {recipient.email} is not possible: {e}") 
            

async def send_mail(r : str, message):
    smtp_client = aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT, use_tls=True)
    await smtp_client.connect()
    await smtp_client.login(EMAIL_SENDER, EMAIL_PASSWORD)
    try:
        logger.info("Start mail to ------------- " , r)
        await smtp_client.send_message(message)
        logger.info("End mail to ------------- " , r)
    except Exception as e:
        logger.info("Error mail to ------------- " , r, " ", e)
        return False, str(e)
    finally:
        await smtp_client.quit()
    return True, None
    