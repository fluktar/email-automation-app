class ContactsManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def add_contact(self, email, name):
        with self.db_connection.cursor() as cursor:
            cursor.execute("INSERT INTO contacts (email, name) VALUES (%s, %s)", (email, name))
            self.db_connection.commit()

    def remove_contact(self, email):
        with self.db_connection.cursor() as cursor:
            cursor.execute("DELETE FROM contacts WHERE email = %s", (email,))
            self.db_connection.commit()

    def get_contacts(self):
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT email, name FROM contacts")
            return cursor.fetchall()