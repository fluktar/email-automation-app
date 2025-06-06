import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import psycopg2

# Wczytaj zmienne środowiskowe z .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..','..', '.env'))


SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = int(os.getenv('SSH_PORT', 22))
SSH_USER = os.getenv('SSH_USER')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Ustawienia tunelu SSH
def test_db_connection():
    with SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PASSWORD,
        remote_bind_address=(DB_HOST, DB_PORT)
    ) as tunnel:
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print('Połączenie OK, wersja PostgreSQL:', version)
        cur.close()
        conn.close()

if __name__ == '__main__':
    test_db_connection()
