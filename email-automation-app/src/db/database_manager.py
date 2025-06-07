import os
from dotenv import load_dotenv, find_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2


class DatabaseManager:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.ssh_host = os.getenv("SSH_HOST")
        self.ssh_port = int(os.getenv("SSH_PORT", 22))
        self.ssh_user = os.getenv("SSH_USER")
        self.ssh_password = os.getenv("SSH_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = int(os.getenv("DB_PORT", 5432))
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")

    def _get_connection(self):
        tunnel = SSHTunnelForwarder(
            (self.ssh_host, self.ssh_port),
            ssh_username=self.ssh_user,
            ssh_password=self.ssh_password,
            remote_bind_address=(self.db_host, self.db_port),
        )
        tunnel.start()
        conn = psycopg2.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
        )
        return conn, tunnel
