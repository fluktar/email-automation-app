import os
from dotenv import load_dotenv
import paramiko

# Wczytaj dane z .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = int(os.getenv('SSH_PORT', 22))
SSH_USER = os.getenv('SSH_USER')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')
NAS_PATH = os.getenv('NAS_PATH')

class AttachmentUploader:
    @staticmethod
    def upload(local_path, remote_filename=None):
        if not remote_filename:
            remote_filename = os.path.basename(local_path)
        if NAS_PATH.endswith('/'):
            remote_path = NAS_PATH + remote_filename
        else:
            remote_path = NAS_PATH + '/' + remote_filename
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD)
            sftp = ssh.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return remote_path
        finally:
            ssh.close()
