import os
from dotenv import load_dotenv


load_dotenv()


POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')  
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

SERVER_URL = os.getenv('SERVER_URL', 'http://server.com')

REDIRECT_URL = os.getenv('REDIRECT_URL', 'https://google.de')


SMTP_SERVER = os.getenv('SMTP_HOST', 'localhost')
SMTP_PORT   = int(os.getenv('SMTP_PORT', 25))

EMAIL_SENDER = os.getenv('SENDER', 'your-email@example.com')
EMAIL_PASSWORD = os.getenv('PASSWORD', 'yourPassword')

EMAIL_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'recipients.txt')

SUBJECT_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'subject.txt')

REDIRECT_URL_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'redirect_url.txt')

PIECHART_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'public', 'piechart.png')

EMAIL_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'templates', 'mail.html')   

#SMTP TLS ?


