from .database_manager import DatabaseManager


class EmailTemplatesManager(DatabaseManager):
    def __init__(self):
        super().__init__()

    def save_template(
        self,
        template_type,
        subject,
        body,
        days_after_previous,
        campaign_id,
        attachment_path=None,
    ):
        print(
            f"[DEBUG] save_template: template_type={template_type}, campaign_id={campaign_id}, subject={subject}"
        )
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO email_templates (template_type, subject, body, days_after_previous, campaign_id, attachment_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (template_type, campaign_id) DO UPDATE SET subject=EXCLUDED.subject, body=EXCLUDED.body, days_after_previous=EXCLUDED.days_after_previous, attachment_path=EXCLUDED.attachment_path
        """,
            (
                template_type,
                subject,
                body,
                days_after_previous,
                campaign_id,
                attachment_path,
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()

    def get_templates(self, campaign_id):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT template_type, subject, body, days_after_previous, attachment_path FROM email_templates WHERE campaign_id=%s ORDER BY id;",
            (campaign_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tunnel.stop()
        return rows

    def get_template(self, template_type, campaign_id):
        print(
            f"[DEBUG] get_template: template_type={template_type}, campaign_id={campaign_id}"
        )
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT subject, body, days_after_previous, attachment_path FROM email_templates WHERE template_type=%s AND campaign_id=%s;",
            (template_type, campaign_id),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        tunnel.stop()
        print(f"[DEBUG] get_template: wynik={row}")
        return row
