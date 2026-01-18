@echo off
title ATM Eta Setup

echo [System] Starting Environment Setup...

:: [1]: Check Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 goto NO_PYTHON

:: [2]: Check .venv Existence
if exist .venv goto VENV_EXISTS

:: [3]: Create Virtual Environment
echo [System] Creating virtual environment (.venv)...
python -m venv .venv
if not exist .venv goto VENV_FAIL
echo [System] .venv created successfully.
goto INSTALL_PACKAGES

:VENV_EXISTS
echo [System] Virtual environment (.venv) already exists.

:INSTALL_PACKAGES
:: [4]: Activate Virtual Environment and Install Requirements
echo [System] Activating .venv and installing requirements...
call .venv\Scripts\activate.bat

:: [5]: Upgrade PIP
python -m pip install --upgrade pip

:: [6]: Install Requirements.txt
if exist requirements.txt (
    pip install -r requirements.txt
    goto SUCCESS
) else (
    goto NO_REQ_FILE
)

:SUCCESS
echo.
echo -------------------------------------------------------
echo [Success] Setup Completed! 
echo Now you can run 'run.bat'.
pause
exit

:NO_PYTHON
echo.
echo [ERROR] Python is not found!
echo Please install Python and check "Add to PATH".
pause
exit

:VENV_FAIL
echo.
echo [ERROR] Failed to create virtual environment.
pause
exit

:NO_REQ_FILE
echo.
echo [WARNING] requirements.txt not found.
echo Virtual environment is ready, but no packages were installed.
pause
exit