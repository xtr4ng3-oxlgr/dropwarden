@echo off
title DROPWARDEN
color 0C
cd /d "%~dp0"
mode con: cols=132 lines=42

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 dropwarden.py
    pause
    exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
    python dropwarden.py
    pause
    exit /b
)

echo No se encontro Python instalado.
pause
