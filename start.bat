@echo off
REM Check if Node.js is installed
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Installing...
    powershell -Command "Start-BitsTransfer -Source https://nodejs.org/dist/v18.18.2/node-v18.18.2-x64.msi -Destination nodejs_installer.msi"
    if exist nodejs_installer.msi (
        msiexec /i nodejs_installer.msi /quiet /norestart
        if %errorlevel% neq 0 (
            echo Node.js installation failed. Exiting.
            pause
            exit /b 1
        )
        del nodejs_installer.msi
    ) else (
        echo Failed to download Node.js installer.
        pause
        exit /b 1
    )
)

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing...
    powershell -Command "Start-BitsTransfer -Source https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -Destination python_installer.exe"
    if exist python_installer.exe (
        python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        if %errorlevel% neq 0 (
            echo Python installation failed. Exiting.
            pause
            exit /b 1
        )
        del python_installer.exe
    ) else (
        echo Failed to download Python installer.
        pause
        exit /b 1
    )
)

REM Navigate to backend folder
set BASEDIR=%~dp0
cd /d "%BASEDIR%FastAPI"
if not exist requirements.txt (
    echo Backend directory or requirements.txt is missing. Check your setup.
    pause
    exit /b 1
)

REM Set up and run backend
if not exist "env\Scripts\activate.bat" (
    python -m venv env
    call env\Scripts\activate
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo pip install failed. Check your requirements file.
        pause
        exit /b 1
    )
)


start cmd /k "cd /d %BASEDIR%FastAPI && python -m uvicorn main:app --reload"

REM Navigate to frontend folder
cd /d "%BASEDIR%React\pdf-converter"

start cmd /k "cd /d %BASEDIR%React\pdf-converter && npm start"

REM Notify user
echo Both backend and frontend have been started in separate terminals.
pause
