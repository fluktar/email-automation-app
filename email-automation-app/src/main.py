# filepath: email-automation-app/email-automation-app/src/main.py

import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__)))

from gui_app import EmailAutomationApp

if __name__ == "__main__":
    app = EmailAutomationApp()
    app.mainloop()
