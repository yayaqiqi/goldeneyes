@echo off
:start
python main.py
echo programme exit, 5 seconds later restarts...
timeout /t 5 /nobreak >nul
goto start
