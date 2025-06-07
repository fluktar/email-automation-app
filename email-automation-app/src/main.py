# filepath: email-automation-app/email-automation-app/src/main.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from db.contacts_manager import ContactsManager
from db.campaign_steps_manager import CampaignStepsManager
from db.campaigns_manager import CampaignsManager
from db.attachments_manager import AttachmentsManager
from db.attachment_uploader import AttachmentUploader
from db.campaign_progress_manager import CampaignProgressManager
from db.email_templates_manager import EmailTemplatesManager
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import datetime
import traceback
from imapclient import IMAPClient

class EmailAutomationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Email Automation App')
        self.geometry('1200x900')
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
        self.steps_manager = CampaignStepsManager()
        self.campaigns_manager = CampaignsManager()
        self.attachments_manager = AttachmentsManager()
        self.attachment_uploader = AttachmentUploader()

        main_frame = ttk.Frame(self.tab_messages)
        main_frame.pack(fill='both', expand=True)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Lista kampanii
        ttk.Label(left_frame, text='Kampanie:').pack(anchor='w')
        self.campaign_listbox = tk.Listbox(left_frame, width=25)
        self.campaign_listbox.pack(fill='x', pady=(0, 10))
        self.campaign_listbox.bind('<<ListboxSelect>>', self.on_campaign_select_messages)
        add_camp_frame = ttk.Frame(left_frame)
        add_camp_frame.pack(fill='x', pady=(0, 10))
        self.new_campaign_entry = ttk.Entry(add_camp_frame, width=15)
        self.new_campaign_entry.pack(side='left', padx=2)
        ttk.Button(add_camp_frame, text='Dodaj', command=self.add_campaign).pack(side='left')
        ttk.Button(left_frame, text='Usuń', command=self.remove_campaign).pack(pady=2)
        self.campaigns = []
        self.selected_campaign_id = None
        self.load_campaigns()

        # Lista kroków kampanii
        ttk.Label(left_frame, text='Kroki kampanii:').pack(anchor='w', pady=(10, 0))
        self.steps_listbox = tk.Listbox(left_frame, width=25, exportselection=False)
        self.steps_listbox.pack(fill='x')
        self.steps_listbox.bind('<<ListboxSelect>>', self.on_step_select)
        self.steps_listbox.config(state='disabled')
        self.current_step_id = None
        self.steps = []
        # Dodawanie/usuwanie kroków
        steps_btn_frame = ttk.Frame(left_frame)
        steps_btn_frame.pack(fill='x', pady=(5, 0))
        ttk.Button(steps_btn_frame, text='Dodaj krok', command=self.add_step).pack(side='left', padx=2)
        ttk.Button(steps_btn_frame, text='Usuń krok', command=self.remove_step).pack(side='left', padx=2)

        # Prawa strona: formularz
        self.template_form_frame = ttk.Frame(right_frame)
        self.template_form_frame.pack(fill='both', expand=True)
        self.subject_entry = ttk.Entry(self.template_form_frame, width=60)
        self.body_text = tk.Text(self.template_form_frame, wrap='word')
        self.days_entry = ttk.Entry(self.template_form_frame, width=10)
        # --- Sekcja załączników ---
        self.attachments_section = ttk.Frame(self.template_form_frame)
        self.attachments_label = ttk.Label(self.attachments_section, text='Załączniki:')
        self.attachments_label.pack(anchor='w')
        self.attachments_listbox = tk.Listbox(self.attachments_section, width=50, height=8)
        self.attachments_listbox.pack(fill='x', pady=(2,2))
        btns_frame = ttk.Frame(self.attachments_section)
        btns_frame.pack(anchor='w', pady=2)
        self.add_attachment_btn = ttk.Button(btns_frame, text='Dodaj załącznik', command=self.add_attachment)
        self.add_attachment_btn.pack(side='left', padx=2)
        self.remove_attachment_btn = ttk.Button(btns_frame, text='Usuń załącznik', command=self.remove_attachment)
        self.remove_attachment_btn.pack(side='left', padx=2)
        self.save_btn = ttk.Button(self.template_form_frame, text='Zapisz', command=self.save_current_step)
        self.disable_template_form()

        # Komunikaty
        self.message_status_label = ttk.Label(self.tab_messages, text='', foreground='green')
        self.message_status_label.pack(side='bottom', pady=5)

    def load_campaigns(self):
        self.campaigns = self.campaigns_manager.get_campaigns()
        self.campaign_listbox.delete(0, 'end')
        for _id, name in self.campaigns:
            self.campaign_listbox.insert('end', name)

    def add_campaign(self):
        name = self.new_campaign_entry.get().strip()
        if name:
            self.campaigns_manager.add_campaign(name)
            self.load_campaigns()
            self.new_campaign_entry.delete(0, 'end')

    def remove_campaign(self):
        selection = self.campaign_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        camp_id, camp_name = self.campaigns[idx]
        self.campaigns_manager.remove_campaign(camp_name)
        self.load_campaigns()
        if hasattr(self, 'steps_listbox'):
            self.steps_listbox.delete(0, 'end')
            self.steps_listbox.config(state='disabled')
        self.current_step_id = None
        self.disable_template_form()

    def on_campaign_select_messages(self, event):
        selection = self.campaign_listbox.curselection()
        if not selection:
            self.selected_campaign_id = None
            self.steps_listbox.config(state='disabled')
            self.disable_template_form()
            return
        idx = selection[0]
        camp_id, camp_name = self.campaigns[idx]
        self.selected_campaign_id = camp_id
        self.load_steps()
        self.steps_listbox.config(state='normal')
        self.steps_listbox.selection_clear(0, 'end')
        self.current_step_id = None
        self.disable_template_form()

    def load_steps(self):
        self.steps = self.steps_manager.get_steps(self.selected_campaign_id)
        self.steps_listbox.delete(0, 'end')
        for step in self.steps:
            _id, order, name, *_ = step
            self.steps_listbox.insert('end', f'{order}. {name}')

    def add_step(self):
        if not self.selected_campaign_id:
            self.show_message_status('Najpierw wybierz kampanię!', 'red')
            return
        from tkinter.simpledialog import askstring
        name = askstring('Nowy krok', 'Podaj nazwę kroku:')
        if name:
            self.steps_manager.add_step(self.selected_campaign_id, name)
            self.load_steps()

    def remove_step(self):
        selection = self.steps_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        step_id = self.steps[idx][0]
        self.steps_manager.remove_step(step_id)
        self.load_steps()
        self.disable_template_form()

    def on_step_select(self, event):
        if not self.selected_campaign_id:
            self.disable_template_form()
            return
        selection = self.steps_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        step = self.steps[idx]
        if self.current_step_id == step[0]:
            return
        self.current_step_id = step[0]
        self.show_step_form(step)

    def show_step_form(self, step):
        for widget in self.template_form_frame.winfo_children():
            widget.pack_forget()
        ttk.Label(self.template_form_frame, text='Temat:').pack(anchor='w')
        self.subject_entry.pack(fill='x', pady=2)
        ttk.Label(self.template_form_frame, text='Treść:').pack(anchor='w')
        self.body_text.pack(fill='both', expand=True, pady=2)
        ttk.Label(self.template_form_frame, text='Dni po poprzedniej:').pack(anchor='w')
        self.days_entry.pack(anchor='w', pady=2)
        # --- Sekcja załączników ---
        self.attachments_section.pack(fill='x', pady=(10,0))
        self.save_btn.pack(pady=10)
        self.template_form_frame.pack(fill='both', expand=True)
        self.load_current_step()
        self.load_attachments()
        self.enable_template_form()

    def load_attachments(self):
        self.attachments_listbox.delete(0, 'end')
        self.current_attachments = []
        if not self.current_step_id:
            return
        attachments = self.attachments_manager.get_attachments(self.current_step_id)
        for att in attachments:
            att_id, filename, remote_path = att
            self.attachments_listbox.insert('end', filename)
            self.current_attachments.append({'id': att_id, 'filename': filename, 'remote_path': remote_path})

    def add_attachment(self):
        if not self.current_step_id:
            self.show_message_status('Najpierw wybierz krok!', 'red')
            return
        file_path = filedialog.askopenfilename(filetypes=[('PDF files', '*.pdf'), ('All files', '*.*')])
        if not file_path:
            return
        filename = os.path.basename(file_path)
        try:
            remote_path = self.attachment_uploader.upload(file_path, filename)
            self.attachments_manager.add_attachment(self.current_step_id, filename, remote_path)
            self.show_message_status('Załącznik dodany!')
            self.load_attachments()
        except Exception as e:
            self.show_message_status(f'Błąd: {e}', 'red')

    def remove_attachment(self):
        selection = self.attachments_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        att = self.current_attachments[idx]
        self.attachments_manager.remove_attachment(att['id'])
        self.show_message_status('Załącznik usunięty!')
        self.load_attachments()

    def disable_template_form(self):
        for widget in self.template_form_frame.winfo_children():
            widget.pack_forget()
        self.template_form_frame.pack_forget()
        self.subject_entry.delete(0, 'end')
        self.body_text.delete('1.0', 'end')
        self.days_entry.delete(0, 'end')
        self.attachments_listbox.delete(0, 'end')

    def enable_template_form(self):
        self.template_form_frame.pack(fill='both', expand=True)

    def load_current_step(self):
        if not self.current_step_id:
            self.subject_entry.delete(0, 'end')
            self.body_text.delete('1.0', 'end')
            self.days_entry.delete(0, 'end')
            return
        step = next((s for s in self.steps if s[0] == self.current_step_id), None)
        if not step:
            self.subject_entry.delete(0, 'end')
            self.body_text.delete('1.0', 'end')
            self.days_entry.delete(0, 'end')
            return
        _, _, name, subject, body, days, _ = step
        self.subject_entry.delete(0, 'end')
        self.subject_entry.insert(0, subject or '')
        self.body_text.delete('1.0', 'end')
        self.body_text.insert('1.0', body or '')
        self.days_entry.delete(0, 'end')
        self.days_entry.insert(0, str(days) if days is not None else '')

    def save_current_step(self):
        if not self.current_step_id:
            self.show_message_status('Najpierw wybierz krok!', 'red')
            return
        subject = self.subject_entry.get().strip()
        body = self.body_text.get('1.0', 'end').strip()
        try:
            days = int(self.days_entry.get().strip())
        except ValueError:
            days = None
        self.steps_manager.update_step(self.current_step_id, subject, body, days, None)
        steps = self.steps_manager.get_steps(self.selected_campaign_id)
        if steps and steps[0][0] == self.current_step_id:
            if not hasattr(self, 'templates_manager'):
                self.templates_manager = EmailTemplatesManager()
            # Ustaw days=0 jeśli None dla szablonu powitalnego
            welcome_days = days if days is not None else 0
            self.templates_manager.save_template(
                'welcome', subject, body, welcome_days, self.selected_campaign_id, None
            )
        self.show_message_status('Krok został zapisany!')
        self.load_steps()

    def choose_attachment_single(self):
        pass  # NIEUŻYWANE, zostawiamy pustą dla kompatybilności

    def init_analytics_tab(self):
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

        # Etykieta statusu wysyłki
        self.send_status_label = ttk.Label(right_frame, text='', foreground='blue')
        self.send_status_label.pack(pady=2)

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
        threading.Thread(target=self._run_campaign_send_thread, daemon=True).start()

    def _run_campaign_send_thread(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import EMAIL_CONFIG
        if not self.selected_analytics_campaign_id:
            self.send_status_label.config(text='Błąd: wybierz kampanię!')
            self.after(2000, lambda: self.send_status_label.config(text=''))
            return
        contacts_manager = ContactsManager()
        contacts = contacts_manager.get_contacts()
        progress_rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
        progressed_emails = {row[1]: row for row in progress_rows}
        templates_manager = EmailTemplatesManager()
        tpl = templates_manager.get_template('welcome', self.selected_analytics_campaign_id)
        if not tpl:
            self.send_status_label.config(text='Brak szablonu powitalnego!')
            self.after(2000, lambda: self.send_status_label.config(text=''))
            return
        subject, body, *_ = tpl
        steps = self.steps_manager.get_steps(self.selected_analytics_campaign_id)
        if not steps:
            self.send_status_label.config(text='Brak kroków w tej kampanii!')
            self.after(2000, lambda: self.send_status_label.config(text=''))
            return
        welcome_step_id = steps[0][0]
        attachments = self.attachments_manager.get_attachments(welcome_step_id)
        sent_count = 0
        # --- WYSYŁKA WSZYSTKICH ETAPÓW KAMPANII ---
        steps = self.steps_manager.get_steps(self.selected_analytics_campaign_id)
        if not steps:
            self.send_status_label.config(text='Brak kroków w tej kampanii!')
            self.after(2000, lambda: self.send_status_label.config(text=''))
            return
        sent_count = 0
        # Odśwież postęp po każdej wysyłce, by nie wysyłać ponownie do tych samych kontaktów
        progress_rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
        progressed_emails = {row[1]: row for row in progress_rows}
        for idx, contact in enumerate(contacts):
            contact_id, email, company, address, phone, contact_name = contact
            row = progressed_emails.get(email)
            if not row:
                continue
            stage = row[3]
            last_send = row[4]
            response = row[5]
            # Nie wysyłaj jeśli kontakt odpowiedział
            if stage == 'responded':
                continue
            # Ustal na którym etapie jest kontakt
            current_step_idx = 0
            if stage == 'welcome_sent':
                current_step_idx = 1
            elif stage == 'reminder_sent':
                current_step_idx = 2
            elif stage == 'last_offer_sent':
                current_step_idx = 3
            # Jeśli jesteśmy poza liczbą kroków, pomiń
            if current_step_idx >= len(steps):
                continue
            # Sprawdź czy minęło odpowiednio dużo dni od ostatniej wysyłki
            step = steps[current_step_idx]
            step_id, step_order, name, subject, body, days_after_prev, _ = step
            if current_step_idx == 0:
                # Pierwszy krok: wyślij jeśli not_sent
                if stage == 'not_sent':
                    try:
                        self.send_status_label.config(text=f'Wysyłam do: {email} ({idx+1}/{len(contacts)})')
                        self.update_idletasks()
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_CONFIG['from_address']
                        msg['To'] = email
                        msg['Subject'] = subject
                        msg.attach(MIMEText(body, 'plain'))
                        attachments = self.attachments_manager.get_attachments(step_id)
                        for att in attachments:
                            _, filename, remote_path = att
                            if os.path.isfile(remote_path):
                                with open(remote_path, 'rb') as f:
                                    part = MIMEBase('application', 'octet-stream')
                                    part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                                msg.attach(part)
                        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
                        server.starttls()
                        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                        server.sendmail(EMAIL_CONFIG['from_address'], email, msg.as_string())
                        server.quit()
                        now = datetime.datetime.now()
                        self.analytics_progress_manager.add_or_update_progress(
                            self.selected_analytics_campaign_id, contact_id, 'welcome_sent', now
                        )
                        sent_count += 1
                        # Odśwież postęp po zmianie
                        progress_rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
                        progressed_emails = {row[1]: row for row in progress_rows}
                    except Exception as e:
                        self.send_status_label.config(text=f'Błąd wysyłki do {email}: {e}')
                        self.update_idletasks()
            else:
                # Kolejne kroki: wyślij jeśli minęło odpowiednio dużo dni od last_send
                if last_send is not None and days_after_prev is not None:
                    last_send_dt = last_send if isinstance(last_send, datetime.datetime) else datetime.datetime.strptime(str(last_send), '%Y-%m-%d %H:%M:%S')
                    if (datetime.datetime.now() - last_send_dt).days >= days_after_prev:
                        try:
                            self.send_status_label.config(text=f'Wysyłam do: {email} ({idx+1}/{len(contacts)}) - {name}')
                            self.update_idletasks()
                            msg = MIMEMultipart()
                            msg['From'] = EMAIL_CONFIG['from_address']
                            msg['To'] = email
                            msg['Subject'] = subject
                            msg.attach(MIMEText(body, 'plain'))
                            attachments = self.attachments_manager.get_attachments(step_id)
                            for att in attachments:
                                _, filename, remote_path = att
                                if os.path.isfile(remote_path):
                                    with open(remote_path, 'rb') as f:
                                        part = MIMEBase('application', 'octet-stream')
                                        part.set_payload(f.read())
                                    encoders.encode_base64(part)
                                    part.add_header('Content-Disposition', f'attachment; filename={filename}')
                                    msg.attach(part)
                            server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
                            server.starttls()
                            server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
                            server.sendmail(EMAIL_CONFIG['from_address'], email, msg.as_string())
                            server.quit()
                            now = datetime.datetime.now()
                            # Ustal nowy status
                            if current_step_idx == 1:
                                new_stage = 'reminder_sent'
                            elif current_step_idx == 2:
                                new_stage = 'last_offer_sent'
                            else:
                                new_stage = stage
                            self.analytics_progress_manager.add_or_update_progress(
                                self.selected_analytics_campaign_id, contact_id, new_stage, now
                            )
                            sent_count += 1
                            # Odśwież postęp po zmianie
                            progress_rows = self.analytics_progress_manager.get_progress_for_campaign(self.selected_analytics_campaign_id)
                            progressed_emails = {row[1]: row for row in progress_rows}
                        except Exception as e:
                            self.send_status_label.config(text=f'Błąd wysyłki do {email}: {e}')
                            self.update_idletasks()
        self.send_status_label.config(text='Wysyłka zakończona!')
        self.load_campaign_progress()
        self.after(3000, lambda: self.send_status_label.config(text=''))
        messagebox.showinfo('Wysyłka', f'Wysłano {sent_count} wiadomości w tej turze!')

    def check_responses(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import EMAIL_CONFIG

        if not self.selected_analytics_campaign_id:
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

        # Sprawdź czy dane IMAP są ustawione
        imap_host = EMAIL_CONFIG.get('imap_server', EMAIL_CONFIG['smtp_server'])
        imap_user = EMAIL_CONFIG.get('username')
        imap_pass = EMAIL_CONFIG.get('password')
        if not imap_host or not imap_user or not imap_pass:
            messagebox.showerror('Błąd IMAP', 'Brak danych logowania do serwera IMAP w pliku .env lub config.py!')
            return
        try:
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
            messagebox.showinfo('Odpowiedzi', 'Sprawdzono odpowiedzi w skrzynce odbiorczej!')
        except Exception as e:
            messagebox.showerror('Błąd IMAP', f'Nie udało się połączyć z serwerem IMAP:\n{e}')

    def on_progress_row_double_click(self, event):
        item = self.progress_tree.selection()
        if not item:
            return
        values = self.progress_tree.item(item[0], 'values')
        email = values[0]
        stage = values[2]
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from config import EMAIL_CONFIG
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

    def show_message_status(self, text, color='green'):
        self.message_status_label.config(text=text, foreground=color)
        self.message_status_label.after(4000, lambda: self.message_status_label.config(text=''))

if __name__ == '__main__':
    app = EmailAutomationApp()
    app.mainloop()