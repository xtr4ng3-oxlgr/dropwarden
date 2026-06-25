@echo off
title DROPWARDEN - Build C entropy helper
color 0C
cd /d "%~dp0"

where gcc >nul 2>nul
if %errorlevel% neq 0 (
    echo No se encontro gcc.
    echo Este helper es opcional. DROPWARDEN funciona igual con Python.
    pause
    exit /b
)

gcc entropy.c -O2 -o entropy.exe
pause
