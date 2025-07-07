from db.contacts_manager import ContactsManager
from tkinter import ttk


class ContactsController:
    def __init__(self, gui):
        self.gui = gui

    def init_addresses_tab(self):
        self.gui.contacts_manager = ContactsManager()
        form_frame = ttk.Frame(self.gui.tab_addresses)
        form_frame.pack(pady=10, anchor="w")
        ttk.Label(form_frame, text="Email:").grid(row=0, column=0, padx=5, pady=5)
        self.gui.email_entry = ttk.Entry(form_frame, width=30)
        self.gui.email_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Nazwa firmy:").grid(row=1, column=0, padx=5, pady=5)
        self.gui.company_entry = ttk.Entry(form_frame, width=30)
        self.gui.company_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Adres:").grid(row=2, column=0, padx=5, pady=5)
        self.gui.address_entry = ttk.Entry(form_frame, width=30)
        self.gui.address_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Telefon:").grid(row=3, column=0, padx=5, pady=5)
        self.gui.phone_entry = ttk.Entry(form_frame, width=30)
        self.gui.phone_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(form_frame, text="Imię i nazwisko kontaktu:").grid(
            row=4, column=0, padx=5, pady=5
        )
        self.gui.contact_name_entry = ttk.Entry(form_frame, width=30)
        self.gui.contact_name_entry.grid(row=4, column=1, padx=5, pady=5)
        add_btn = ttk.Button(form_frame, text="Dodaj", command=self.add_contact)
        add_btn.grid(row=5, column=0, columnspan=2, pady=10)
        self.gui.contacts_list = ttk.Treeview(
            self.gui.tab_addresses,
            columns=("email", "company", "address", "phone", "contact_name"),
            show="headings",
        )
        self.gui.contacts_list.heading("email", text="Email")
        self.gui.contacts_list.heading("company", text="Nazwa firmy")
        self.gui.contacts_list.heading("address", text="Adres")
        self.gui.contacts_list.heading("phone", text="Telefon")
        self.gui.contacts_list.heading("contact_name", text="Imię i nazwisko kontaktu")
        self.gui.contacts_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_contacts_list()

    def add_contact(self):
        email = self.gui.email_entry.get().strip()
        company = self.gui.company_entry.get().strip()
        address = self.gui.address_entry.get().strip()
        phone = self.gui.phone_entry.get().strip()
        contact_name = self.gui.contact_name_entry.get().strip()
        if email:
            self.gui.contacts_manager.add_contact(
                email, company, address, phone, contact_name
            )
            self.gui.email_entry.delete(0, "end")
            self.gui.company_entry.delete(0, "end")
            self.gui.address_entry.delete(0, "end")
            self.gui.phone_entry.delete(0, "end")
            self.gui.contact_name_entry.delete(0, "end")
            self.refresh_contacts_list()

    def refresh_contacts_list(self):
        for row in self.gui.contacts_list.get_children():
            self.gui.contacts_list.delete(row)
        for (
            _id,
            email,
            company,
            address,
            phone,
            contact_name,
        ) in self.gui.contacts_manager.get_contacts():
            self.gui.contacts_list.insert(
                "", "end", values=(email, company, address, phone, contact_name)
            )
