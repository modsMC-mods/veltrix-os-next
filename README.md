# VELTRIX OS Next

Rozszerzalny desktop w Pythonie/PyQt6. To aplikacja uruchamiana na Linuksie lub Windowsie, nie osobny kernel.

## Windows: launcher ze przyciskiem START

1. Zainstaluj Python 3.10+ z https://www.python.org/downloads/ i zaznacz **Add python.exe to PATH**.
2. Utwórz środowisko i zainstaluj zależności:

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Dwukrotnie kliknij `launcher.bat` lub uruchom:

```bat
py launcher.py
```

Pojawi się małe okno ze przyciskiem **START**. Po jego naciśnięciu uruchomi się VELTRIX OS.

Możesz też użyć `run.bat`, uruchamiając projekt bez okna launchera.

## Komenda CMD

Po uruchomieniu `install-command.bat` zamknij i otwórz ponownie CMD, a następnie wpisz:

```bat
veltrix
```

## Linux

```bash
chmod +x run.sh
./run.sh
```
