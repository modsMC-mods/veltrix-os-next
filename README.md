# VELTRIX OS Next

Rozszerzalny desktop w Pythonie/PyQt6. To aplikacja uruchamiana na Linuksie lub Windowsie, nie osobny kernel.

## Windows: łatwa komenda `veltrix`

1. Zainstaluj Python 3.10+ z https://www.python.org/downloads/ i zaznacz **Add Python to PATH**.
2. W katalogu repozytorium kliknij dwukrotnie `install-command.bat`. Skrypt utworzy komendę i doda ją do PATH użytkownika.
3. Zamknij i otwórz ponownie CMD.
4. Wpisz:

```bat
veltrix
```

Aby zainstalować/zaktualizować środowisko projektu, najpierw uruchom w katalogu repozytorium:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Możesz też użyć `run.bat` do instalacji zależności i uruchomienia bez konfigurowania komendy.

## Linux

```bash
chmod +x run.sh
./run.sh
```

## Diagnostyka

Uruchom `veltrix` w CMD, aby zobaczyć błędy. Log startowy znajduje się w `~/.local/state/veltrix-os/startup.log`.
