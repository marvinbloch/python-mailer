import asyncio
import io
from typing import List



from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles

from .utils.piechart import create_piechart
from .models.models import Email, EmailHistory
from .config.database import get_task_db, init_db, engine, get_track_db, get_sending_task_db, get_laoding_task_db, get_updating_task_db
from .services.crud import get_all_emails, get_all_sendable_emails, get_histories_by_email_id
from .tasks.sender_task import send_emails_task
from .tasks.loading_task import load_emails_to_database_task
from .config.logging_setup import logger
from .tasks.update_reachable_task import update_reachable_emails_task
from .utils.tracking import track_click_func
from .config.config import WAIT_TIME

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

app.mount("/public", StaticFiles(directory="src/public"), name="public")

action_lock = asyncio.Lock()
current_task = None
total_emails = 0
emails_sent = 0

@app.on_event("startup")
async def on_startup():
    await init_db()
    logger.info("Application startup: Database initialized")

@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()
    logger.info("Application shutdown: Database engine disposed")

@app.get("/", response_class=HTMLResponse)
async def root_page(request: Request, db: AsyncSession = Depends(get_task_db)):
    emails = await get_all_emails(db)

    formatted_emails = []

    total_clicks = 0
    total_attempts = 0
    clicked_emails = 0
    not_clicked_emails = 0
    not_valid_emails = 0
    not_reachable_emails = 0
    not_send_emails = 0
    successfully_send_emails = 0


    for email in emails:
        histories: List[EmailHistory] = await get_histories_by_email_id(db, email.id)
        email_attempts = len(histories) if histories else 0
        email_clicks = sum(history.click_count for history in histories) if histories else 0
        success_attempts = sum((1 if history.success else 0) for history in histories) if histories else 0

        if not email.valid:
            not_valid_emails += 1
        elif not email.reachable:
            not_reachable_emails += 1
        elif email_attempts == 0:
            not_send_emails += 1
        else:
            total_attempts += email_attempts
            total_clicks += email_clicks
            successfully_send_emails += 1
            if email_clicks > 0:
                clicked_emails += 1
            else: 
                not_clicked_emails += 1

        formatted_emails.append({
            "email": email.email,
            "valid": email.valid,
            "reachable": email.reachable,
            "click_count": email_clicks,
            "success_attempts": success_attempts,
            "attempts": email_attempts
        })

   
    stats = {
        "total_attempts": total_attempts,
        "total_clicks": total_clicks,
        "clicked_emails": clicked_emails,
        "not_clicked_emails": not_clicked_emails,
        "not_reachable_emails": not_reachable_emails,
        "not_valid_emails": not_valid_emails,
        "not_send_emails": not_send_emails,
        "successfully_send_emails": successfully_send_emails
    }

    return templates.TemplateResponse("index.html", {"request": request, "emails": formatted_emails, "stats": stats})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    print("FAV ICON")
    return FileResponse("src/public/favicon.ico")

@app.get("/clicks_piechart")
async def clicks_piechart(db: AsyncSession = Depends(get_task_db)):
    await create_piechart(db)
    return FileResponse("src/public/piechart.png")

def convert_seconds(sec):
    days = sec // (24 * 3600)
    sec %= (24 * 3600)
    hours = sec // 3600
    sec %= 3600
    minutes = sec // 60
    sec %= 60
    seconds = sec
    return days, hours, minutes, seconds

@app.get("/task_status", response_class=JSONResponse)
async def get_task_status():
    global current_task, total_emails, emails_sent
    if action_lock.locked():
        if ("Sending" in current_task.capitalize()):
            remaining_emails = total_emails - emails_sent
            estimated_time_seconds  = remaining_emails * (WAIT_TIME + 1)
            days, hours, minutes, seconds = convert_seconds(estimated_time_seconds)
            time_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
            return JSONResponse(status_code=200, content={
                "message": f"Current task: {current_task.capitalize()} is running. \n {remaining_emails} emails left to send {emails_sent} / {total_emails}. \n Estimated time remaining: {time_str}."
            })
        else:
            return JSONResponse(status_code=200, content={"message": f"Current task: {current_task.capitalize()} is running"})
    else:
        return JSONResponse(status_code=200, content={"message": "The system is free"})
    
async def update_progress():
    global emails_sent
    emails_sent += 1

@app.post("/sendEmails", response_class=JSONResponse)
async def send_emails_endpoint(db: AsyncSession = Depends(get_sending_task_db)):
    global current_task, total_emails, emails_sent
    if action_lock.locked():
        return JSONResponse(status_code=429, content={"message": f"{current_task.capitalize()} Task is already running. Please wait until it finishes."})

    async with action_lock:
        current_task="sending"
        emails_sent = 0
        logger.info("Send only emails, marked as sendable, from the database")
        await asyncio.sleep(1) 
        recipients: List[Email] = await get_all_sendable_emails(db)
        total_emails = len(recipients)
        result = await send_emails_task(db, recipients, update_progress)
        current_task = None
        status_code = 200 if not result["error"] else 500
        return JSONResponse(status_code=status_code, content=result)

async def has_no_successfull_attempts(db: AsyncSession, email_id: int) -> bool:
    histories = await get_histories_by_email_id(db, email_id)
    success_attempts = sum((1 if history.success else 0) for history in histories) if histories else 0
    return success_attempts == 0  

@app.post("/sendEmailsWithNoAttempts", response_class=JSONResponse)
async def send_emails_with_no_attempts_endpoint(db: AsyncSession = Depends(get_sending_task_db)):
    global current_task, total_emails, emails_sent
    if action_lock.locked():
        return JSONResponse(status_code=429, content={"message": f"{current_task.capitalize()} Task is already running. Please wait until it finishes."})

    async with action_lock:
        current_task="sending no attempts"
        emails_sent = 0
        logger.info("Send only emails, marked as sendable and having no attempts, from the database")
        await asyncio.sleep(1) 
        recipients: List[Email] = await get_all_sendable_emails(db)
        recipients_with_no_attempts: List[Email] = [recipient for recipient in recipients if await has_no_successfull_attempts(db, recipient.id)]
        total_emails = len(recipients_with_no_attempts)
        result = await send_emails_task(db, recipients_with_no_attempts, update_progress)
        current_task = None
        status_code = 200 if not result["error"] else 500
        return JSONResponse(status_code=status_code, content=result)

@app.post("/loadEmails", response_class=JSONResponse)
async def send_emails_endpoint(db: AsyncSession = Depends(get_laoding_task_db)):
    global current_task
    if action_lock.locked():
        return JSONResponse(status_code=429, content={"message": f"{current_task.capitalize()} Task is already running. Please wait until it finishes."})

    async with action_lock:
        current_task="loading"
        logger.info("Loading emails into the database")
        await asyncio.sleep(1) 
        result = await load_emails_to_database_task(db)
        current_task = None
        status_code = 200 if not result["error"] else 500
        return JSONResponse(status_code=status_code, content={"message": "Emails loaded successfully"})

@app.post("/updateReachable", response_class=JSONResponse)
async def update_reachable_endpoint(db: AsyncSession = Depends(get_updating_task_db)):
    global current_task
    if action_lock.locked():
        return JSONResponse(status_code=429, content={"message": f"{current_task.capitalize()} Task is already running. Please wait until it finishes."})

    async with action_lock:
        current_task="updating"
        logger.info("Updating reachable status for emails")
        await asyncio.sleep(1) 
        result = await update_reachable_emails_task(db)
        current_task = None
        status_code = 200 if not result["error"] else 500
        return JSONResponse(status_code=status_code, content=result)

@app.get("/{tracking_id}")
async def track_click(tracking_id: str, request: Request, db: AsyncSession = Depends(get_track_db)):
   return await track_click_func(tracking_id, request, db)



