import re
import dns.asyncresolver
from dataclasses import dataclass
from ..config.logging_setup import logger

from ..models.models import Email

async def validate_email_format(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(regex, email):
        logger.info(f"Successfully validate the Email: {email}")
        return True
    else:
        logger.info(f"Not a valid Email: {email}")
    return False

async def check_mx_records(domain):
    try:
        resolver = dns.asyncresolver.Resolver()
        await resolver.resolve(domain, 'MX')
        logger.info(f"Successfully resolve the Domain - {domain}")
        return True
    except Exception as e:
        logger.info(f"Unsuccessfully resolve the Domain - {domain}: {e}")
        return False

@dataclass
class EmailCheckResult:
    valid: bool
    reachable: bool

async def check_email(email) -> EmailCheckResult:
    valid = await validate_email_format(email)
    reachable = False
    if valid:
        domain = email.split('@')[1]
        reachable = await check_mx_records(domain)
    return EmailCheckResult(valid, reachable)

async def check_reachable(email) -> bool:
    result: EmailCheckResult = await check_email(email)
    return result.reachable
    
async def initial_email(email: str) -> Email:
    result: EmailCheckResult = await check_email(email)
    return Email(
        email=email,
        reachable=result.reachable,
        valid=result.valid
    )