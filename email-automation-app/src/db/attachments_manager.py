import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2
from .database_manager import DatabaseManager


class AttachmentsManager(DatabaseManager):
    def __init__(self):
        super().__init__()

    def get_attachments(self, step_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, filename, remote_path FROM attachments WHERE step_id = %s",
            (step_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def add_attachment(self, step_id, filename, remote_path):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO attachments (step_id, filename, remote_path) VALUES (%s, %s, %s)",
            (step_id, filename, remote_path),
        )
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def remove_attachment(self, attachment_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM attachments WHERE id = %s", (attachment_id,))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
