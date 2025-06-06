import tkinter as tk
from tkinter import messagebox
from faker import Faker
from sshtunnel import SSHTunnelForwarder
import psycopg2
import os
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'src', '..', '.env'))
SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = int(os.getenv('SSH_PORT', 22))
SSH_USER = os.getenv('SSH_USER')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

class DemoDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Demo Data Generator (PostgreSQL)')
        self.geometry('400x180')
        self.fake = Faker('pl_PL')
        self.create_widgets()

    def _get_connection(self):
        tunnel = SSHTunnelForwarder(
            (SSH_HOST, SSH_PORT),
            ssh_username=SSH_USER,
            ssh_password=SSH_PASSWORD,
            remote_bind_address=(DB_HOST, DB_PORT)
        )
        tunnel.start()
        conn = psycopg2.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn, tunnel

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(expand=True)
        btn_generate = tk.Button(frame, text='Generuj 20 kontaktów demo', width=35, command=self.generate_contacts)
        btn_generate.pack(pady=10)
        btn_clear = tk.Button(frame, text='Wyczyść wszystkie kontakty', width=35, command=self.clear_contacts)
        btn_clear.pack(pady=10)

    def generate_contacts(self):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        for _ in range(20):
            email = self.fake.unique.email()
            company = self.fake.company()
            address = self.fake.address().replace('\n', ' ')
            phone = self.fake.phone_number()
            contact_name = self.fake.name()
            cur.execute('''
                INSERT INTO email_addresses (email, company_name, address, phone, contact_name)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING;
            ''', (email, company, address, phone, contact_name))
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
        messagebox.showinfo('Sukces', 'Dodano 200 przykładowych kontaktów do bazy!')

    def clear_contacts(self):
        conn, tunnel = self._get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM email_addresses')
        conn.commit()
        cur.close()
        conn.close()
        tunnel.stop()
        messagebox.showinfo('Sukces', 'Wyczyszczono wszystkie kontakty z bazy!')

if __name__ == '__main__':
    app = DemoDataApp()
    app.mainloop()
