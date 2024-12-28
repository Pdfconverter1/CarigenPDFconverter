::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAnk
::fBw5plQjdG8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSDk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+JeA==
::cxY6rQJ7JhzQF1fEqQJQ
::ZQ05rAF9IBncCkqN+0xwdVs0
::ZQ05rAF9IAHYFVzEqQJQ
::eg0/rx1wNQPfEVWB+kM9LVsJDGQ=
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQJQ
::dhA7uBVwLU+EWDk=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATElA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFDVbXg2+GG6pDaET+NTM4PiMnn05cuEwdpneyKCLMtwg/kT2Ydgozn86
::YB416Ek+ZG8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off

REM Navigate to backend folder
set BASEDIR=%~dp0
cd /d "%BASEDIR%FastAPI"
if not exist requirements.txt (
    echo Backend directory or requirements.txt is missing. Check your setup.
    pause
    exit /b 1
)

REM Set up and run backend
    
pip install -r requirements.txt
if %errorlevel% neq 0 (
   echo pip install failed. Check your requirements file.
   pause
   exit /b 1
  )


start cmd /k "cd /d %BASEDIR%FastAPI && python -m uvicorn main:app --reload"

REM Navigate to frontend folder
cd /d "%BASEDIR%React\pdf-converter"

start cmd /k "cd /d %BASEDIR%React\pdf-converter && npm start"

REM Notify user
echo Both backend and frontend have been started in separate terminals.
pause
