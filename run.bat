@echo off
cd /d "%~dp0"

venv\Scripts\python.exe popro_control\popro_start.py

echo.
echo ------------------------------
echo 終了コード: %errorlevel%
pause