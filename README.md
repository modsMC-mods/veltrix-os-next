# VELTRIX OS Next

Rozszerzalny desktop w Pythonie/PyQt6. To aplikacja uruchamiana na Linuksie lub Windowsie, nie osobny kernel.

## Windows (uruchamianie kliknięciem)

Zainstaluj Python 3.10+ z https://www.python.org/downloads/ i zaznacz **Add Python to PATH**. Następnie kliknij dwukrotnie `run.bat`. Skrypt tworzy środowisko `.venv`, instaluje wymagania i uruchamia pulpit. Okno konsoli pozostaje otwarte po zamknięciu lub błędzie, więc komunikat nie znika.

Możesz też uruchomić w terminalu:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m veltrix
```

## Linux

```bash
chmod +x run.sh
./run.sh
```

## Diagnostyka

Jeśli aplikacja nadal się zamyka, uruchom `run.bat` z CMD/PowerShell i skopiuj pełny komunikat błędu. Ślad startowy zapisywany jest w `~/.local/state/veltrix-os/startup.log` (na Windows w katalogu domowym użytkownika).
