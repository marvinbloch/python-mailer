import logging
import os

log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

def setup_logging():
    # Create a logger
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)
    
    # Create a file handler
    file_handler = logging.FileHandler(os.path.join(log_directory, 'app.log'))
    file_handler.setLevel(logging.INFO)
    
    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()
