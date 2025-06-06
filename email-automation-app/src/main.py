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
        from db.email_templates_manager import EmailTemplatesManager
        self.templates_manager = EmailTemplatesManager()

        self.template_types = [
            ('welcome', 'Powitalna z ofertą'),
            ('reminder', 'Przypominająca'),
            ('last_offer', 'Ostatnia propozycja')
        ]
        self.template_vars = {}
        self.subject_entries = {}
        self.body_texts = {}
        self.days_entries = {}

        for idx, (typ, label) in enumerate(self.template_types):
            frame = ttk.LabelFrame(self.tab_messages, text=label)
            frame.pack(fill='x', padx=10, pady=10)

            ttk.Label(frame, text='Temat:').grid(row=0, column=0, sticky='w')
            subject_entry = ttk.Entry(frame, width=60)
            subject_entry.grid(row=0, column=1, padx=5, pady=2)
            self.subject_entries[typ] = subject_entry

            ttk.Label(frame, text='Treść:').grid(row=1, column=0, sticky='nw')
            body_text = tk.Text(frame, width=60, height=4)
            body_text.grid(row=1, column=1, padx=5, pady=2)
            self.body_texts[typ] = body_text

            ttk.Label(frame, text='Dni po poprzedniej:').grid(row=2, column=0, sticky='w')
            days_entry = ttk.Entry(frame, width=10)
            days_entry.grid(row=2, column=1, sticky='w', padx=5, pady=2)
            self.days_entries[typ] = days_entry

            save_btn = ttk.Button(frame, text='Zapisz', command=lambda t=typ: self.save_template(t))
            save_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.load_templates()

    def save_template(self, template_type):
        subject = self.subject_entries[template_type].get().strip()
        body = self.body_texts[template_type].get('1.0', 'end').strip()
        try:
            days = int(self.days_entries[template_type].get().strip())
        except ValueError:
            days = 0
        if subject and body:
            self.templates_manager.save_template(template_type, subject, body, days)

    def load_templates(self):
        for typ, _ in self.template_types:
            tpl = self.templates_manager.get_template(typ)
            if tpl:
                subject, body, days = tpl
                self.subject_entries[typ].delete(0, 'end')
                self.subject_entries[typ].insert(0, subject)
                self.body_texts[typ].delete('1.0', 'end')
                self.body_texts[typ].insert('1.0', body)
                self.days_entries[typ].delete(0, 'end')
                self.days_entries[typ].insert(0, str(days))

    def init_analytics_tab(self):
        label = ttk.Label(self.tab_analytics, text='Moduł analityczny')
        label.pack(pady=10)
        # Tu dodamy dalszą logikę i widżety

if __name__ == '__main__':
    app = EmailAutomationApp()
    app.mainloop()