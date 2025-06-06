# filepath: email-automation-app/email-automation-app/src/main.py

import tkinter as tk
from tkinter import ttk

class EmailAutomationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Email Automation App')
        self.geometry('800x600')
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        # Moduł 1: Dodawanie adresów email
        self.tab_addresses = ttk.Frame(notebook)
        notebook.add(self.tab_addresses, text='Adresy email')
        self.init_addresses_tab()

        # Moduł 2: Tworzenie wiadomości
        self.tab_messages = ttk.Frame(notebook)
        notebook.add(self.tab_messages, text='Wiadomości')
        self.init_messages_tab()

        # Moduł 3: Analityka
        self.tab_analytics = ttk.Frame(notebook)
        notebook.add(self.tab_analytics, text='Analityka')
        self.init_analytics_tab()

    def init_addresses_tab(self):
        from db.contacts_manager import ContactsManager
        self.contacts_manager = ContactsManager()

        form_frame = ttk.Frame(self.tab_addresses)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text='Email:').grid(row=0, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(form_frame, width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text='Nazwa firmy:').grid(row=1, column=0, padx=5, pady=5)
        self.company_entry = ttk.Entry(form_frame, width=30)
        self.company_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text='Adres:').grid(row=2, column=0, padx=5, pady=5)
        self.address_entry = ttk.Entry(form_frame, width=30)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text='Telefon:').grid(row=3, column=0, padx=5, pady=5)
        self.phone_entry = ttk.Entry(form_frame, width=30)
        self.phone_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text='Imię i nazwisko kontaktu:').grid(row=4, column=0, padx=5, pady=5)
        self.contact_name_entry = ttk.Entry(form_frame, width=30)
        self.contact_name_entry.grid(row=4, column=1, padx=5, pady=5)

        add_btn = ttk.Button(form_frame, text='Dodaj', command=self.add_contact)
        add_btn.grid(row=5, column=0, columnspan=2, pady=10)

        self.contacts_list = ttk.Treeview(
            self.tab_addresses,
            columns=('email', 'company', 'address', 'phone', 'contact_name'),
            show='headings'
        )
        self.contacts_list.heading('email', text='Email')
        self.contacts_list.heading('company', text='Nazwa firmy')
        self.contacts_list.heading('address', text='Adres')
        self.contacts_list.heading('phone', text='Telefon')
        self.contacts_list.heading('contact_name', text='Imię i nazwisko kontaktu')
        self.contacts_list.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh_contacts_list()

    def add_contact(self):
        email = self.email_entry.get().strip()
        company = self.company_entry.get().strip()
        address = self.address_entry.get().strip()
        phone = self.phone_entry.get().strip()
        contact_name = self.contact_name_entry.get().strip()
        if email:
            self.contacts_manager.add_contact(email, company, address, phone, contact_name)
            self.email_entry.delete(0, 'end')
            self.company_entry.delete(0, 'end')
            self.address_entry.delete(0, 'end')
            self.phone_entry.delete(0, 'end')
            self.contact_name_entry.delete(0, 'end')
            self.refresh_contacts_list()

    def refresh_contacts_list(self):
        for row in self.contacts_list.get_children():
            self.contacts_list.delete(row)
        for _id, email, company, address, phone, contact_name in self.contacts_manager.get_contacts():
            self.contacts_list.insert('', 'end', values=(email, company, address, phone, contact_name))

    def init_messages_tab(self):
        label = ttk.Label(self.tab_messages, text='Tworzenie i zarządzanie wiadomościami')
        label.pack(pady=10)
        # Tu dodamy dalszą logikę i widżety

    def init_analytics_tab(self):
        label = ttk.Label(self.tab_analytics, text='Moduł analityczny')
        label.pack(pady=10)
        # Tu dodamy dalszą logikę i widżety

if __name__ == '__main__':
    app = EmailAutomationApp()
    app.mainloop()