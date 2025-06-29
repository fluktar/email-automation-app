# Modularna aplikacja GUI (TODO, YouTube Downloader, Pogoda, Kalendarz, Notatki)

## Opis

Nowoczesna, modularna aplikacja desktopowa (Tkinter, Python) z obsługą wielu modułów:

- **TODO** (lista zadań, załączniki, PostgreSQL przez SSH, SFTP)
- **YouTube Downloader** (GUI, wybór formatu, katalogu, obsługa ffmpeg)
- **Pogoda** (moduł w przygotowaniu)
- **Kalendarz/Terminarz** (moduł w przygotowaniu)
- **Notatki** (moduł w przygotowaniu)

Aplikacja posiada ciemny motyw, nowoczesny wygląd, dynamiczny wybór modułów przez kafelki z ikonami.

## Struktura projektu

```
app/
├── main.py                # Główny plik uruchamiający aplikację
├── base_module.py         # Klasa bazowa dla modułów
├── modules/
│   ├── todoList/          # Moduł TODO (zadania, załączniki, baza)
│   ├── ytdownload/        # Moduł YouTube Downloader
│   ├── weather.py         # Moduł Pogoda (placeholder)
│   ├── calendar.py        # Moduł Kalendarz (placeholder)
│   ├── notes.py           # Moduł Notatki (placeholder)
│   └── ...                # Inne moduły
└── ...
```

## Instalacja

1. Sklonuj repozytorium:
   ```
   git clone <repo-url>
   ```
2. Przejdź do katalogu projektu:
   ```
   cd app
   ```
3. Zainstaluj wymagane biblioteki:
   ```
   pip install -r requirements.txt
   ```

## Konfiguracja

- Skonfiguruj pliki środowiskowe `.env` oraz pliki `settings.json`/`user_paths.json` w odpowiednich modułach (np. ytdownload).
- Ustaw dane do bazy PostgreSQL i SFTP w module TODO (patrz pliki w `modules/todoList`).

## Użytkowanie

Aby uruchomić aplikację, użyj polecenia:

```
python -m app.main
```

## Funkcje

- Wybór modułu przez nowoczesny panel kafelków z ikonami
- TODO: lista zadań, załączniki, paginacja, rejestracja/logowanie, PostgreSQL przez SSH, SFTP
- YouTube Downloader: pobieranie wideo/audio, wybór formatu, katalogu, obsługa ffmpeg
- Pogoda, Kalendarz, Notatki: placeholdery do dalszej rozbudowy
- Ciemny motyw, nowoczesny UI

## Wkład

Wszelkie sugestie i poprawki są mile widziane. Proszę o zgłaszanie problemów lub propozycji zmian w sekcji Issues.
