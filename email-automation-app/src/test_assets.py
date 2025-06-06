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

TEST_LOCAL_FILE = 'test.pdf'  # Plik PDF do testu (umieść w tym samym folderze co ten skrypt)


def test_nas_upload_via_ssh():
    print(f"Próba połączenia SSH z {SSH_HOST}:{SSH_PORT} jako {SSH_USER}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASSWORD)
        sftp = ssh.open_sftp()        # Użyj ścieżki UNIX (nie os.path.join na Windows!)
        if NAS_PATH.endswith('/'):
            remote_path = NAS_PATH + TEST_LOCAL_FILE
        else:
            remote_path = NAS_PATH + '/' + TEST_LOCAL_FILE
        print(f"Wysyłanie pliku {TEST_LOCAL_FILE} na serwer przez SSH do {remote_path}")
        sftp.put(TEST_LOCAL_FILE, remote_path)
        print("Plik wysłany pomyślnie! (pełna ścieżka: {} )".format(remote_path))
        sftp.close()
    except Exception as e:
        print(f"Błąd podczas wysyłania pliku przez SSH: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    test_nas_upload_via_ssh()
