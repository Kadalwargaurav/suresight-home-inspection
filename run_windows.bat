@echo off
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if "%SURESIGHT_SECRET_KEY%"=="" set SURESIGHT_SECRET_KEY=change-this-before-public-deployment
if "%SURESIGHT_ADMIN_PASSWORD%"=="" set SURESIGHT_ADMIN_PASSWORD=ChangeMe-Now-123!
python app.py
pause
