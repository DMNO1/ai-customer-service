@echo off
REM AI Customer Service System - Startup Script for Windows

echo Starting AI Customer Service System...

REM Set environment variables
set FLASK_APP=updated_main_service.py
set PORT=8000

REM Navigate to the project directory
cd /d "C:\Users\91780\.openclaw\workspace\business\ai-customer-service"

REM Run the main service
echo Running AI Customer Service on port %PORT%...
python updated_main_service.py

pause