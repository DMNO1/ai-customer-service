@echo off
chcp 65001 >nul
title AI Customer Service - Enhanced Version

echo ====================================================
echo AI Customer Service System - Enhanced Edition
echo ====================================================
echo.

REM Check Python availability
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ and ensure 'py' command is available.
    pause
    exit /b 1
)

echo [1/5] Checking dependencies...
py -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo [2/5] Setting up environment...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [INFO] Created .env file from example. Please edit .env to configure your settings.
    ) else (
        echo [WARNING] No .env.example found. Please create .env manually.
    )
) else (
    echo [OK] .env file already exists
)

echo [3/5] Checking database connection...
REM You may want to add a more thorough DB check here
echo [INFO] Ensure PostgreSQL is running and DATABASE_URL is set in .env

echo [4/5] Initializing vector database...
if not exist "chroma_db" (
    echo [INFO] Creating vector database directory...
    mkdir chroma_db
)
echo [OK] Vector database ready

echo [5/5] Starting services...
echo.
echo ====================================================
echo Starting Enhanced AI Customer Service...
echo.
echo Configuration Tips:
echo   - Set OPENAI_API_KEY, ANTHROPIC_API_KEY for AI models
echo   - Set FEISHU_APP_ID and FEISHU_APP_SECRET for notifications
echo   - Set DATABASE_URL for PostgreSQL connection
echo   - Set payment keys (ALIPAY_APP_ID, etc.) for billing
echo.
echo Press Ctrl+C to stop the service
echo ====================================================
echo.

py main_service_enhanced.py

pause