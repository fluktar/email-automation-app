import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2

class EmailTemplatesManager:
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
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

    def save_template(self, template_type, subject, body, days_after_previous):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO email_templates (template_type, subject, body, days_after_previous)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (template_type) DO UPDATE SET subject=EXCLUDED.subject, body=EXCLUDED.body, days_after_previous=EXCLUDED.days_after_previous;
        ''', (template_type, subject, body, days_after_previous))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def get_templates(self):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('SELECT template_type, subject, body, days_after_previous FROM email_templates ORDER BY id;')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def get_template(self, template_type):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('SELECT subject, body, days_after_previous FROM email_templates WHERE template_type=%s;', (template_type,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        tunnel.stop()
        return row
