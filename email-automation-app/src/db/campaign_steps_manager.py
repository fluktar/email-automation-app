import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2

class CampaignStepsManager:
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

    def get_steps(self, campaign_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT id, step_order, name, subject, body, days_after_prev, attachment_path
            FROM campaign_steps
            WHERE campaign_id = %s
            ORDER BY step_order
        ''', (campaign_id,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def add_step(self, campaign_id, name, step_order=None):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        if step_order is None:
            cur.execute('SELECT COALESCE(MAX(step_order), 0) + 1 FROM campaign_steps WHERE campaign_id = %s', (campaign_id,))
            step_order = cur.fetchone()[0]
        cur.execute('''
            INSERT INTO campaign_steps (campaign_id, step_order, name)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (campaign_id, step_order, name))
        step_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
        return step_id

    def remove_step(self, step_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM campaign_steps WHERE id = %s', (step_id,))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def update_step(self, step_id, subject, body, days_after_prev, attachment_path):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('''
            UPDATE campaign_steps
            SET subject=%s, body=%s, days_after_prev=%s, attachment_path=%s
            WHERE id=%s
        ''', (subject, body, days_after_prev, attachment_path, step_id))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
