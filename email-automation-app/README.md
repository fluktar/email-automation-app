# Email Automation App

## Opis
Aplikacja do automatyzacji wysyłania wiadomości e-mail, która monitoruje odpowiedzi, wysyła przypomnienia do tych, którzy nie odpowiedzieli, oraz integruje się z bazą danych w celu zarządzania kontaktami.

## Struktura projektu
```
email-automation-app
├── src
│   ├── main.py                # Punkt wejścia aplikacji
│   ├── email_sender.py        # Klasa do wysyłania wiadomości e-mail
│   ├── reminder.py            # Klasa do zarządzania przypomnieniami
│   ├── response_monitor.py     # Klasa do monitorowania odpowiedzi
│   ├── db
│   │   ├── __init__.py        # Inicjalizacja modułu bazy danych
│   │   └── contacts_manager.py # Klasa do zarządzania kontaktami
│   └── config.py              # Konfiguracje aplikacji
├── requirements.txt           # Zależności projektu
└── README.md                  # Dokumentacja projektu
```

## Instalacja
1. Sklonuj repozytorium:
   ```
   git clone <repo-url>
   ```
2. Przejdź do katalogu projektu:
   ```
   cd email-automation-app
   ```
3. Zainstaluj wymagane biblioteki:
   ```
   pip install -r requirements.txt
   ```

## Konfiguracja
Skonfiguruj plik `src/config.py`, aby ustawić dane logowania do serwera e-mail oraz parametry bazy danych.

## Użytkowanie
Aby uruchomić aplikację, użyj polecenia:
```
python src/main.py
```

## Wkład
Wszelkie sugestie i poprawki są mile widziane. Proszę o zgłaszanie problemów lub propozycji zmian w sekcji Issues.