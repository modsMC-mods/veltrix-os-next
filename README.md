# VELTRIX OS Next

Rozszerzalny desktop w Pythonie/PyQt6. To aplikacja uruchamiana na Linuksie lub Windowsie, nie osobny kernel.

## Windows: launcher ze przyciskiem START

1. Zainstaluj Python 3.10+ z https://www.python.org/downloads/ i zaznacz **Add python.exe to PATH**.
2. Dwukrotnie kliknij `launcher.bat`.
3. Kliknij **START**. Launcher sam utworzy `.venv`, doinstaluje pakiety z `requirements.txt` i uruchomi pulpit. Pierwsze uruchomienie może potrwać.

Jeśli wystąpi błąd, launcher pokaże komunikat. Szczegóły zapisuje do `veltrix-launcher.log` w katalogu projektu. Zachowuje okno launchera, żeby można było ponowić próbę.

Możesz również uruchomić z CMD:

```bat
py launcher.py
```

## Linux

```bash
chmod +x run.sh
./run.sh
```
