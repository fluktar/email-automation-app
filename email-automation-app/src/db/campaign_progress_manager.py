import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2

class CampaignProgressManager:
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

    def get_progress_for_campaign(self, campaign_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT cp.id, ea.email, ea.company_name, cp.current_stage, cp.last_send_date, cp.response_date
            FROM campaign_progress cp
            JOIN email_addresses ea ON cp.contact_id = ea.id
            WHERE cp.campaign_id = %s
            ORDER BY ea.email
        ''', (campaign_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def add_or_update_progress(self, campaign_id, contact_id, stage, last_send_date=None, response_date=None):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO campaign_progress (campaign_id, contact_id, current_stage, last_send_date, response_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (campaign_id, contact_id) DO UPDATE SET current_stage=EXCLUDED.current_stage, last_send_date=EXCLUDED.last_send_date, response_date=EXCLUDED.response_date;
        ''', (campaign_id, contact_id, stage, last_send_date, response_date))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
