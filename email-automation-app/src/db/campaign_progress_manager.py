import os
from dotenv import load_dotenv
from .database_manager import DatabaseManager


class CampaignProgressManager(DatabaseManager):
    def __init__(self):
        super().__init__()

    def get_progress_for_campaign(self, campaign_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT cp.id, ea.email, ea.company_name, cp.current_stage, cp.last_send_date, cp.response_date
            FROM campaign_progress cp
            JOIN email_addresses ea ON cp.contact_id = ea.id
            WHERE cp.campaign_id = %s
            ORDER BY cp.id
        """,
            (campaign_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def add_or_update_progress(
        self, campaign_id, contact_id, stage, last_send_date=None, response_date=None
    ):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO campaign_progress (campaign_id, contact_id, current_stage, last_send_date, response_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (campaign_id, contact_id) DO UPDATE SET current_stage=EXCLUDED.current_stage, last_send_date=EXCLUDED.last_send_date, response_date=EXCLUDED.response_date;
        """,
            (campaign_id, contact_id, stage, last_send_date, response_date),
        )
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
