# This file contains configuration settings for the email automation application.

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..','..' '.env'))

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}

EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('EMAIL_USERNAME'),
    'password': os.getenv('EMAIL_PASSWORD'),
    'from_address': os.getenv('EMAIL_FROM'),
    'imap_server': os.getenv('IMAP_SERVER'),
}

REMINDER_SETTINGS = {
    'reminder_interval': 7,  # days
    'reminder_subject': 'Friendly Reminder',
    'reminder_body': 'This is a reminder to respond to our previous email.'
}

# Additional configurations can be added as needed.