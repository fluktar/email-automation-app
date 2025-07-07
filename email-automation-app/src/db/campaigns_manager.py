from .database_manager import DatabaseManager


class CampaignsManager(DatabaseManager):
    def __init__(self):
        super().__init__()

    def add_campaign(self, name):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO campaigns (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
            (name,),
        )
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def remove_campaign(self, name):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM campaigns WHERE name=%s;", (name,))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def get_campaigns(self):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM campaigns ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows
