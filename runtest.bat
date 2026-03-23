@echo off
chcp 65001 >nul
cd /d "%~dp0"
py validate_imports.py
pause