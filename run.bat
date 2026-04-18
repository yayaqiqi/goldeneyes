@echo off
:start
python main.py
echo 程序退出，5秒后重启...
timeout /t 5 /nobreak >nul
goto start
