import os
from dotenv import load_dotenv
from .database_manager import DatabaseManager


class ContactsManager(DatabaseManager):
    def __init__(self):
        super().__init__()

    def add_contact(
        self, email, company_name=None, address=None, phone=None, contact_name=None
    ):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO email_addresses (email, company_name, address, phone, contact_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """,
            (email, company_name, address, phone, contact_name),
        )
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def get_contacts(self):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, company_name, address, phone, contact_name FROM email_addresses ORDER BY id DESC;"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows
