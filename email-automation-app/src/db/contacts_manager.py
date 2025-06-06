import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2

class ContactsManager:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(__file__), '..','..', '.env'))
        self.ssh_host = os.getenv('SSH_HOST')
        self.ssh_port = int(os.getenv('SSH_PORT', 22))
        self.ssh_user = os.getenv('SSH_USER')
        self.ssh_password = os.getenv('SSH_PASSWORD')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = int(os.getenv('DB_PORT', 5432))
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')

    def _get_connection(self):
        tunnel = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_password=self.ssh_password,
            remote_bind_address=(self.db_host, self.db_port)
        )
        tunnel.start()
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        return conn, tunnel

    def add_contact(self, email, company_name=None, address=None, phone=None, contact_name=None):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO email_addresses (email, company_name, address, phone, contact_name)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        ''', (email, company_name, address, phone, contact_name))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def get_contacts(self):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, email, company_name, address, phone, contact_name FROM email_addresses ORDER BY id DESC;')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows