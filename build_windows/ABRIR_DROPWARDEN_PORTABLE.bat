@echo off
title DROPWARDEN
color 0C
cd /d "%~dp0"
mode con: cols=132 lines=42

if exist "DROPWARDEN\DROPWARDEN.exe" (
    "DROPWARDEN\DROPWARDEN.exe"
    pause
    exit /b
)

echo No se encontro DROPWARDEN\DROPWARDEN.exe
pause
