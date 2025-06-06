# filepath: email-automation-app/email-automation-app/src/main.py

import tkinter as tk
from tkinter import ttk
import os

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
        form_frame.pack(pady=10, anchor='w')

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
        from tkinter import filedialog, messagebox
        from db.email_templates_manager import EmailTemplatesManager
        from db.campaigns_manager import CampaignsManager
        self.templates_manager = EmailTemplatesManager()
        self.campaigns_manager = CampaignsManager()

        # --- Panel kampanii po prawej stronie ---
        main_frame = ttk.Frame(self.tab_messages)
        main_frame.pack(fill='both', expand=True)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        right_frame = ttk.Frame(main_frame, width=200)
        right_frame.pack(side='right', fill='y')

        # Lista kampanii
        ttk.Label(right_frame, text='Kampanie:').pack(pady=5)
        self.campaign_listbox = tk.Listbox(right_frame, width=25)
        self.campaign_listbox.pack(padx=5, pady=5, fill='y', expand=True)
        self.campaign_listbox.bind('<<ListboxSelect>>', self.on_campaign_select)

        add_camp_frame = ttk.Frame(right_frame)
        add_camp_frame.pack(pady=5)
        self.new_campaign_entry = ttk.Entry(add_camp_frame, width=15)
        self.new_campaign_entry.pack(side='left', padx=2)
        ttk.Button(add_camp_frame, text='Dodaj', command=self.add_campaign).pack(side='left')
        ttk.Button(right_frame, text='Usuń', command=self.remove_campaign).pack(pady=2)

        self.campaigns = []
        self.selected_campaign_id = None
        self.load_campaigns()

        # --- Szablony wiadomości ---
        self.template_types = [
            ('welcome', 'Powitalna z ofertą'),
            ('reminder', 'Przypominająca'),
            ('last_offer', 'Ostatnia propozycja')
        ]
        self.subject_entries = {}
        self.body_texts = {}
        self.days_entries = {}
        self.attachment_labels = {}
        self.attachment_paths = {}
        self.attachment_buttons = {}
        self.template_frames = {}

        for idx, (typ, label) in enumerate(self.template_types):
            frame = ttk.LabelFrame(left_frame, text=label)
            frame.pack(fill='x', padx=10, pady=10)
            self.template_frames[typ] = frame

            ttk.Label(frame, text='Temat:').grid(row=0, column=0, sticky='w')
            subject_entry = ttk.Entry(frame, width=60)
            subject_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
            self.subject_entries[typ] = subject_entry

            ttk.Label(frame, text='Treść:').grid(row=1, column=0, sticky='nw')
            body_text = tk.Text(frame, wrap='word')
            body_text.grid(row=1, column=1, padx=5, pady=2, sticky='nsew')
            self.body_texts[typ] = body_text
            frame.grid_rowconfigure(1, weight=1)
            frame.grid_columnconfigure(1, weight=1)

            # Dni po poprzedniej tylko dla reminder i last_offer
            if typ != 'welcome':
                ttk.Label(frame, text='Dni po poprzedniej:').grid(row=2, column=0, sticky='w')
                days_entry = ttk.Entry(frame, width=10)
                days_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
                self.days_entries[typ] = days_entry
                row_attach = 3
            else:
                self.days_entries[typ] = None
                row_attach = 2

            # Załącznik
            attach_frame = ttk.Frame(frame)
            attach_frame.grid(row=row_attach, column=0, columnspan=2, sticky='w', pady=2)
            attach_btn = ttk.Button(attach_frame, text='Wybierz załącznik', command=lambda t=typ: self.choose_attachment(t))
            attach_btn.pack(side='left')
            self.attachment_buttons[typ] = attach_btn
            attach_label = ttk.Label(attach_frame, text='Brak załącznika', width=40)
            attach_label.pack(side='left', padx=5)
            self.attachment_labels[typ] = attach_label
            self.attachment_paths[typ] = None

            save_btn = ttk.Button(frame, text='Zapisz', command=lambda t=typ: self.save_template(t))
            save_btn.grid(row=row_attach+1, column=0, columnspan=2, pady=5)

        # Etykieta na komunikaty na dole zakładki
        self.message_status_label = ttk.Label(self.tab_messages, text='', foreground='green')
        self.message_status_label.pack(side='bottom', pady=5)

        self.disable_templates()

    def show_message_status(self, text, color='green'):
        self.message_status_label.config(text=text, foreground=color)
        self.message_status_label.after(4000, lambda: self.message_status_label.config(text=''))

    def choose_attachment(self, template_type):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')])
        if file_path:
            self.attachment_paths[template_type] = file_path
            self.attachment_labels[template_type]['text'] = os.path.basename(file_path)
        else:
            self.attachment_paths[template_type] = None
            self.attachment_labels[template_type]['text'] = 'Brak załącznika'

    def add_campaign(self):
        name = self.new_campaign_entry.get().strip()
        if name:
            self.campaigns_manager.add_campaign(name)
            self.load_campaigns()
            self.new_campaign_entry.delete(0, 'end')

    def remove_campaign(self):
        selection = self.campaign_listbox.curselection()
        if selection:
            idx = selection[0]
            camp_id, camp_name = self.campaigns[idx]
            self.campaigns_manager.remove_campaign(camp_name)
            self.load_campaigns()
            self.disable_templates()

    def load_campaigns(self):
        self.campaigns = self.campaigns_manager.get_campaigns()
        self.campaign_listbox.delete(0, 'end')
        for _id, name in self.campaigns:
            self.campaign_listbox.insert('end', name)

    def on_campaign_select(self, event):
        selection = self.campaign_listbox.curselection()
        if selection:
            idx = selection[0]
            camp_id, camp_name = self.campaigns[idx]
            self.selected_campaign_id = camp_id
            self.enable_templates()
            self.load_templates()
        else:
            self.selected_campaign_id = None
            self.disable_templates()

    def enable_templates(self):
        for typ in self.template_types:
            for widget in self.template_frames[typ[0]].winfo_children():
                if isinstance(widget, (ttk.Entry, tk.Text, ttk.Button)):
                    widget.configure(state='normal')

    def disable_templates(self):
        for typ in self.template_types:
            for widget in self.template_frames[typ[0]].winfo_children():
                if isinstance(widget, (ttk.Entry, tk.Text, ttk.Button)):
                    widget.configure(state='disabled')

    def save_template(self, template_type):
        if not self.selected_campaign_id:
            self.show_message_status('Najpierw wybierz kampanię!', 'red')
            return
        subject = self.subject_entries[template_type].get().strip()
        body = self.body_texts[template_type].get('1.0', 'end').strip()
        if template_type != 'welcome':
            try:
                days = int(self.days_entries[template_type].get().strip())
            except ValueError:
                days = 0
        else:
            days = 0
        attachment_path = self.attachment_paths[template_type]
        self.templates_manager.save_template(
            template_type, subject, body, days, self.selected_campaign_id, attachment_path
        )
        self.show_message_status('Wiadomość została zapisana lub zaktualizowana!')

    def load_templates(self):
        if not self.selected_campaign_id:
            self.disable_templates()
            return
        for typ, _ in self.template_types:
            tpl = self.templates_manager.get_template(typ, self.selected_campaign_id)
            if tpl:
                subject, body, days, attachment_path = tpl
                self.subject_entries[typ].delete(0, 'end')
                self.subject_entries[typ].insert(0, subject)
                self.body_texts[typ].delete('1.0', 'end')
                self.body_texts[typ].insert('1.0', body)
                if typ != 'welcome':
                    self.days_entries[typ].delete(0, 'end')
                    self.days_entries[typ].insert(0, str(days))
                if attachment_path:
                    self.attachment_paths[typ] = attachment_path
                    self.attachment_labels[typ]['text'] = os.path.basename(attachment_path)
                else:
                    self.attachment_paths[typ] = None
                    self.attachment_labels[typ]['text'] = 'Brak załącznika'
            else:
                self.subject_entries[typ].delete(0, 'end')
                self.body_texts[typ].delete('1.0', 'end')
                if typ != 'welcome':
                    self.days_entries[typ].delete(0, 'end')
                self.attachment_paths[typ] = None
                self.attachment_labels[typ]['text'] = 'Brak załącznika'

    def init_analytics_tab(self):
        from db.campaigns_manager import CampaignsManager
        from db.campaign_progress_manager import CampaignProgressManager
        self.analytics_campaigns_manager = CampaignsManager()
        self.analytics_progress_manager = CampaignProgressManager()

        main_frame = ttk.Frame(self.tab_analytics)
        main_frame.pack(fill='both', expand=True)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='y')
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='left', fill='both', expand=True)

        # Lista kampanii
        ttk.Label(left_frame, text='Kampanie:').pack(pady=5)
        self.analytics_campaign_listbox = tk.Listbox(left_frame, width=25)
        self.analytics_campaign_listbox.pack(padx=5, pady=5, fill='y', expand=True)
        self.analytics_campaign_listbox.bind('<<ListboxSelect>>', self.on_analytics_campaign_select)
        self.analytics_campaigns = []
        self.selected_analytics_campaign_id = None
        self.load_analytics_campaigns()

        # Tabela postępu
        columns = ('email', 'company', 'etap', 'ostatnia wysyłka', 'odpowiedź')
        self.progress_tree = ttk.Treeview(right_frame, columns=columns, show='headings')
        for col in columns:
            self.progress_tree.heading(col, text=col)
        self.progress_tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.progress_tree.bind('<Double-1>', self.on_progress_row_double_click)

        # Przycisk uruchamiania wysyłki
        self.send_button = ttk.Button(right_frame, text='Uruchom wysyłkę', command=self.run_campaign_send, state='disabled')
        self.send_button.pack(pady=5)
        # Przycisk sprawdzania odpowiedzi
        self.check_resp_button = ttk.Button(right_frame, text='Sprawdź odpowiedzi', command=self.check_responses, state='disabled')
        self.check_resp_button.pack(pady=5)

    def load_analytics_campaigns(self):
        self.analytics_campaigns = self.analytics_campaigns_manager.get_campaigns()
        self.analytics_campaign_listbox.delete(0, 'end')
        for _id, name in self.analytics_campaigns:
            self.analytics_campaign_listbox.insert('end', name)

    def on_analytics_campaign_select(self, event):
        selection = self.analytics_campaign_listbox.curselection()
        if selection:
            idx = selection[0]
            camp_id, camp_name = self.analytics_campaigns[idx]
            self.selected_analytics_campaign_id = camp_id
            self.load_campaign_progress()
            self.send_button.config(state='normal')
            self.check_resp_button.config(state='normal')
        else:
            self.selected_analytics_campaign_id = None
            self.progress_tree.delete(*self.progress_tree.get_children())
            self.send_button.config(state='disabled')
            self.check_resp_button.config(state='disabled')

    def load_campaign_progress(self):
        self.progress_tree.delete(*self.progress_tree.get_children())
        if not self.selected_analytics_campaign_id:
            return
        rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
        for _id, email, company, stage, last_send, response in rows:
            self.progress_tree.insert('', 'end', values=(email, company, stage, str(last_send) if last_send else '', str(response) if response else ''))

    def run_campaign_send(self):
        from tkinter import messagebox
        from db.email_templates_manager import EmailTemplatesManager
        from db.contacts_manager import ContactsManager
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.base import MIMEBase
        from email import encoders
        import datetime
        import traceback
        # Konfiguracja SMTP z config.py
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import EMAIL_CONFIG

        if not self.selected_analytics_campaign_id:
            messagebox.showerror('Błąd', 'Najpierw wybierz kampanię!')
            return

        # Pobierz kontakty
        contacts_manager = ContactsManager()
        contacts = contacts_manager.get_contacts()
        # Pobierz postęp
        progress_rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
        progressed_emails = {row[1]: row for row in progress_rows}

        # Pobierz szablon powitalny
        templates_manager = EmailTemplatesManager()
        tpl = templates_manager.get_template('welcome', self.selected_analytics_campaign_id)
        if not tpl:
            messagebox.showerror('Błąd', 'Brak szablonu powitalnego dla tej kampanii!')
            return
        subject, body, _, attachment_path = tpl

        sent_count = 0
        for contact in contacts:
            contact_id, email, company, address, phone, contact_name = contact
            # Jeśli kontakt nie ma postępu lub jest na etapie 'not_sent', wyślij powitalną
            row = progressed_emails.get(email)
            if not row or row[3] == 'not_sent':
                try:
                    # Przygotuj wiadomość
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_CONFIG['from_address']
                    msg['To'] = email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))
                    # Załącznik
                    if attachment_path and os.path.isfile(attachment_path):
                        with open(attachment_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
                        msg.attach(part)
                    # Wyślij email
                    server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
                    server.starttls()
                    server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                    server.sendmail(EMAIL_CONFIG['from_address'], email, msg.as_string())
                    server.quit()
                    # Zaktualizuj postęp
                    self.analytics_progress_manager.add_or_update_progress(
                        self.selected_analytics_campaign_id, contact_id, 'welcome_sent', datetime.datetime.now()
                    )
                    sent_count += 1
                except Exception as e:
                    traceback.print_exc()
                    messagebox.showerror('Błąd wysyłki', f'Nie udało się wysłać do {email}: {e}')
        self.load_campaign_progress()
        messagebox.showinfo('Wysyłka', f'Wysłano {sent_count} powitalnych wiadomości!')

    def check_responses(self):
        from imapclient import IMAPClient
        import email
        import datetime
        from db.campaign_progress_manager import CampaignProgressManager
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import EMAIL_CONFIG

        if not self.selected_analytics_campaign_id:
            from tkinter import messagebox
            messagebox.showerror('Błąd', 'Najpierw wybierz kampanię!')
            return

        # Pobierz postęp
        progress_rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
        # Mapuj email -> (contact_id, current_stage)
        email_to_contact = {}
        for row in progress_rows:
            _id, email_addr, company, stage, last_send, response = row
            if stage != 'responded':
                email_to_contact[email_addr.lower()] = (_id, stage)

        # Połącz z IMAP
        imap_host = EMAIL_CONFIG.get('imap_server', EMAIL_CONFIG['smtp_server'])
        imap_user = EMAIL_CONFIG['username']
        imap_pass = EMAIL_CONFIG['password']
        with IMAPClient(imap_host, ssl=True) as server:
            server.login(imap_user, imap_pass)
            server.select_folder('INBOX')
            messages = server.search(['UNSEEN'])
            for uid, message_data in server.fetch(messages, ['ENVELOPE', 'RFC822']).items():
                envelope = message_data[b'ENVELOPE']
                from_addr = envelope.from_[0].mailbox.decode() + '@' + envelope.from_[0].host.decode()
                if from_addr.lower() in email_to_contact:
                    # Zaktualizuj postęp na 'responded'
                    contact_id = _id = email_to_contact[from_addr.lower()][0]
                    self.analytics_progress_manager.add_or_update_progress(
                        self.selected_analytics_campaign_id, contact_id, 'responded', response_date=datetime.datetime.now()
                    )
        self.load_campaign_progress()
        from tkinter import messagebox
        messagebox.showinfo('Odpowiedzi', 'Sprawdzono odpowiedzi w skrzynce odbiorczej!')

    def on_progress_row_double_click(self, event):
        item = self.progress_tree.selection()
        if not item:
            return
        values = self.progress_tree.item(item[0], 'values')
        email = values[0]
        stage = values[2]
        from db.email_templates_manager import EmailTemplatesManager
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import EMAIL_CONFIG
        from imapclient import IMAPClient
        import email as email_mod
        import tkinter as tk
        from tkinter import scrolledtext
        # Domyślnie pokaż ostatnią wysłaną wiadomość (szablon)
        msg_text = ''
        if stage == 'responded':
            # Pobierz najnowszą odpowiedź z IMAP
            imap_host = EMAIL_CONFIG.get('imap_server', EMAIL_CONFIG['smtp_server'])
            imap_user = EMAIL_CONFIG['username']
            imap_pass = EMAIL_CONFIG['password']
            with IMAPClient(imap_host, ssl=True) as server:
                server.login(imap_user, imap_pass)
                server.select_folder('INBOX')
                messages = server.search(['FROM', email])
                if messages:
                    latest_uid = messages[-1]
                    msg_data = server.fetch([latest_uid], ['RFC822'])[latest_uid][b'RFC822']
                    msg = email_mod.message_from_bytes(msg_data)
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == 'text/plain':
                                msg_text = part.get_payload(decode=True).decode(errors='ignore')
                                break
                    else:
                        msg_text = msg.get_payload(decode=True).decode(errors='ignore')
        else:
            # Pobierz szablon ostatniej wysłanej wiadomości
            templates_manager = EmailTemplatesManager()
            tpl = None
            if stage == 'welcome_sent':
                tpl = templates_manager.get_template('welcome', self.selected_analytics_campaign_id)
            elif stage == 'reminder_sent':
                tpl = templates_manager.get_template('reminder', self.selected_analytics_campaign_id)
            elif stage == 'last_offer_sent':
                tpl = templates_manager.get_template('last_offer', self.selected_analytics_campaign_id)
            if tpl:
                subject, body, *_ = tpl
                msg_text = f'Temat: {subject}\n\n{body}'
        # Wyświetl okno z wiadomością
        win = tk.Toplevel(self)
        win.title('Podgląd wiadomości')
        st = scrolledtext.ScrolledText(win, width=80, height=20)
        st.pack(fill='both', expand=True)
        st.insert('1.0', msg_text or 'Brak treści do wyświetlenia.')
        st.config(state='disabled')

if __name__ == '__main__':
    app = EmailAutomationApp()
    app.mainloop()