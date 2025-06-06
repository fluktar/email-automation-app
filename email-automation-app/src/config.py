# This file contains configuration settings for the email automation application.

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'email_automation',
    'user': 'your_username',
    'password': 'your_password'
}

EMAIL_CONFIG = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'username': 'office@uroboros.online',
    'password': 'Sojokotojo1@3',
    'from_address': 'office@uroboros.online'
}

REMINDER_SETTINGS = {
    'reminder_interval': 7,  # days
    'reminder_subject': 'Friendly Reminder',
    'reminder_body': 'This is a reminder to respond to our previous email.'
}

# Additional configurations can be added as needed.