import os
import aiofiles
from ..config.logging_setup import logger



async def read_email_from_files(file_path: str) -> list:
    try:
        if not os.path.isfile(file_path):
            logger.error(f"The File {file_path} does not exist.")
            raise FileNotFoundError(f"The File {file_path} does not exist.")

        async with aiofiles.open(file_path, 'r') as file:
            emails = [line.strip() for line in await file.readlines()]
        logger.info(f"Successfully read emails from {file_path}")
        return emails
    except Exception as e:
        logger.error(f"Failed to read emails from {file_path}: {e}")
        return []
    

async def load_template(template_path: str) -> str:
    return await load_file(template_path, "Template")

async def load_subject(subject_path: str) -> str:
    return await load_file(subject_path, "Subject")

async def load_redirect_url(redirect_url_path: str) -> str:
    return await load_file(redirect_url_path, "Redirect Url")
    
async def load_file(file_path: str, file_type: str) -> str:
    try:
        if not os.path.isfile(file_path):
            logger.error(f"The {file_type} {file_path} does not exist.")
            raise FileNotFoundError(f"The {file_type} {file_path} does not exist.")
        async with aiofiles.open(file_path, 'r') as file:
            content = await file.read()
        logger.info(f"Successfully loaded {file_type} from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Failed to read {file_type} from {file_path}: {e}")
        raise



