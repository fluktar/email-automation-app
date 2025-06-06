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

SQL_PATH = os.path.join(os.path.dirname(__file__), 'init_db.sql')

def run_sql_script():
    with open(SQL_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
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
        cur.execute('BEGIN;')
        cur.execute(sql)
        cur.execute('COMMIT;')
        print('Tabele zostały utworzone lub już istnieją.')
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_sql_script()
