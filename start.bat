@echo off
REM Check if Node.js is installed
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed on this machine.
    echo.
    echo Downloading Node.js installer...

    REM Download the Node.js installer (Windows LTS version)
    powershell -Command "Start-BitsTransfer -Source https://nodejs.org/dist/v18.18.2/node-v18.18.2-x64.msi -Destination nodejs_installer.msi"

    if exist nodejs_installer.msi (
        echo Running Node.js installer...
        msiexec /i nodejs_installer.msi /quiet /norestart
        if %errorlevel% neq 0 (
            echo Failed to install Node.js. Please install manually from https://nodejs.org.
            pause
            exit /b 1
        )
        echo Node.js installed successfully!
        del nodejs_installer.msi
    ) else (
        echo Failed to download Node.js installer. Please install manually from https://nodejs.org.
        pause
        exit /b 1
    )
) else (
    echo Node.js is already installed. Version:
    node -v
)


REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed on this machine.
    echo.
    echo Downloading Python installer...

    REM Download the Python installer (Windows latest version)
    powershell -Command "Start-BitsTransfer -Source https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe -Destination python_installer.exe"

    if exist python_installer.exe (
        echo Running Python installer...
        python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
        if %errorlevel% neq 0 (
            echo Failed to install Python. Please install manually from https://www.python.org.
            pause
            exit /b 1
        )
        echo Python installed successfully!
        del python_installer.exe
    ) else (
        echo Failed to download Python installer. Please install manually from https://www.python.org.
        pause
        exit /b 1
    )
) else (
    echo Python is already installed. Version:
    python --version
)

REM Set up the environment for both backend and frontend

REM Get the directory of the batch file
set BASEDIR=%~dp0

REM Navigate to the backend folder
cd /d "%BASEDIR%FastAPI"
if not exist requirements.txt (
    echo Backend folder is missing or incorrect. Ensure the FastAPI backend folder exists.
    pause
    exit /b 1
)

REM Activate virtual environment
if not exist "env\Scripts\activate.bat" (
    python -m venv env
)
call env\Scripts\activate
pip install -r requirements.txt

REM Start FastAPI backend
start cmd /k "cd /d %BASEDIR%FastAPI && call env\Scripts\activate && python -m uvicorn main:app --reload"

REM Navigate to the frontend folder
cd /d "%BASEDIR%React\pdf-converter"

REM Start React frontend
start cmd /k "cd /d %BASEDIR%React\pdf-converter && npm start"

REM Notify user that processes are starting
echo Both backend and frontend have been started in separate terminals.
pause
