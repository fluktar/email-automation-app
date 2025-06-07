import os
from dotenv import load_dotenv
from .database_manager import DatabaseManager


class CampaignStepsManager(DatabaseManager):
    def __init__(self):
        super().__init__()

    def get_steps(self, campaign_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, step_order, name, subject, body, days_after_prev, attachment_path
            FROM campaign_steps
            WHERE campaign_id = %s
            ORDER BY step_order
        """,
            (campaign_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def add_step(self, campaign_id, name, step_order=None):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        if step_order is None:
            cur.execute(
                "SELECT COALESCE(MAX(step_order), 0) + 1 FROM campaign_steps WHERE campaign_id = %s",
                (campaign_id,),
            )
            step_order = cur.fetchone()[0]
        cur.execute(
            """
            INSERT INTO campaign_steps (campaign_id, step_order, name)
            VALUES (%s, %s, %s)
            RETURNING id
        """,
            (campaign_id, step_order, name),
        )
        step_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
        return step_id

    def remove_step(self, step_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM campaign_steps WHERE id = %s", (step_id,))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def update_step(self, step_id, subject, body, days_after_prev, attachment_path):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE campaign_steps
            SET subject=%s, body=%s, days_after_prev=%s, attachment_path=%s
            WHERE id=%s
        """,
            (subject, body, days_after_prev, attachment_path, step_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
