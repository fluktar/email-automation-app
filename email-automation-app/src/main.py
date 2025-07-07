# filepath: email-automation-app/email-automation-app/src/main.py

import sys
import os

# Dodaj na początku pliku (po importach):
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class EmailAutomationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Email Automation App')
        self.geometry('1200x900')
        self.create_widgets()

sys.path.append(os.path.join(os.path.dirname(__file__)))

from gui_app import EmailAutomationApp

if __name__ == "__main__":
    app = EmailAutomationApp()
    app.mainloop()
