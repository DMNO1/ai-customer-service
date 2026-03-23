@echo off
chcp 65001 >nul
echo Running Quick Test for Enhanced AI Customer Service...
echo.

REM Test import of main modules
echo [TEST] Importing core modules...
py -c "import sys; sys.path.insert(0, 'services'); import llm_provider; import vector_store_service; import document_parser; import web_scraper; import feishu_notifier; print('All core modules imported successfully')"
if errorlevel 1 (
    echo [FAIL] Module import failed
    pause
    exit /b 1
)

echo.
echo [TEST] Checking enhanced main service...
py -c "from main_service_enhanced import EnhancedAICustomerService; print('Enhanced service can be imported')"
if errorlevel 1 (
    echo [FAIL] Enhanced service import failed
    pause
    exit /b 1
)

echo.
echo [TEST] Checking database models...
py -c "import models; print('Models module OK')"
if errorlevel 1 (
    echo [FAIL] Models import failed
    pause
    exit /b 1
)

echo.
echo [TEST] Verifying API module...
py -c "from api.main import app; print('API module OK')"
if errorlevel 1 (
    echo [FAIL] API module import failed
    pause
    exit /b 1
)

echo.
echo ====================================================
echo ALL TESTS PASSED! System is ready to run.
echo ====================================================
echo.
echo Next steps:
echo   1. Copy .env.example to .env and configure your settings
echo   2. Run start_enhanced.bat to start the service
echo   3. Or run: py main_service_enhanced.py
echo.
pause