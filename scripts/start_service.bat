@echo off
echo Starting FAQ Retrieval Service...

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 激活虚拟环境（如果存在）
if exist "%SCRIPT_DIR%..\policy-py\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%SCRIPT_DIR%..\policy-py\.venv\Scripts\activate.bat"
) else (
    echo Virtual environment not found, using system Python...
)

REM 切换到项目目录
cd /d "%SCRIPT_DIR%"

echo Environment setup complete!
echo.

REM 显示菜单
:menu
echo ========================================
echo FAQ Retrieval Service Manager
echo ========================================
echo 1. Start API service
echo 2. Initialize FAQ data via API
echo 3. Test MySQL connection
echo 4. Check service health
echo 5. Exit
echo ========================================
set /p choice="Please select an option (1-5): "

if "%choice%"=="1" goto start_service
if "%choice%"=="2" goto init_via_api
if "%choice%"=="3" goto test_mysql
if "%choice%"=="4" goto check_health
if "%choice%"=="5" goto exit
echo Invalid option, please try again.
goto menu

:start_service
echo.
echo Starting API service...
echo Note: The service will auto-load the embedding model on startup.
echo Once started, you can initialize data via API: POST /api/v1/faqs/initialize
cd /d "%SCRIPT_DIR%.."
python run.py
if %errorlevel% neq 0 (
    echo Failed to start service!
    pause
    goto menu
)
goto menu

:init_via_api
echo.
echo Initializing FAQ data via API...
echo Make sure the API service is running first!
echo Calling: POST http://localhost:5000/api/v1/faqs/initialize
curl -X POST http://localhost:5000/api/v1/faqs/initialize -H "Content-Type: application/json" -d "{\"recreate_collection\": true}"
if %errorlevel% neq 0 (
    echo Failed to initialize via API! Make sure the service is running.
    pause
    goto menu
)
echo Data initialization completed via API!
pause
goto menu

:test_mysql
echo.
echo Testing MySQL connection...
cd /d "%SCRIPT_DIR%.."
python tests\test_mysql.py
if %errorlevel% neq 0 (
    echo MySQL connection test failed!
    pause
    goto menu
)
echo MySQL connection test completed!
pause
goto menu

:check_health
echo.
echo Checking service health...
echo Calling: GET http://localhost:5000/health
curl -X GET http://localhost:5000/health
if %errorlevel% neq 0 (
    echo Health check failed! Make sure the service is running.
    pause
    goto menu
)
echo.
echo Health check completed!
pause
goto menu

:exit
echo Goodbye!
pause
