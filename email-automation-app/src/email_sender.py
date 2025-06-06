class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def prepare_email(self, subject, body, to_addresses):
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))
        return msg

    def send_email(self, subject, body, to_addresses):
        import smtplib

        msg = self.prepare_email(subject, body, to_addresses)
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, to_addresses, msg.as_string())
            print(f"Email sent to: {', '.join(to_addresses)}")
        except Exception as e:
            print(f"Failed to send email: {e}")