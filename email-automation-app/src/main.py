# filepath: email-automation-app/email-automation-app/src/main.py

import sys
from db.contacts_manager import ContactsManager
from email_sender import EmailSender
from reminder import Reminder
from response_monitor import ResponseMonitor
from config import Config

def main():
    # Initialize configuration
    config = Config()

    # Initialize database connection and contacts manager
    contacts_manager = ContactsManager(config.db_settings)
    
    # Load contacts
    contacts = contacts_manager.get_contacts()

    # Initialize email sender
    email_sender = EmailSender(config.email_settings)

    # Send emails to contacts
    for contact in contacts:
        email_sender.send_email(contact)

    # Initialize response monitor
    response_monitor = ResponseMonitor()
    response_monitor.check_responses()

    # Initialize reminder system
    reminder = Reminder()
    reminder.schedule_reminders(contacts)

if __name__ == "__main__":
    main()