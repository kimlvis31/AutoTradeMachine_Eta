@echo off
title ATM Eta Launcher

:: 1. Check Virtual Environment
if exist .venv goto FOUND
echo [ERROR] Virtual Environment (.venv) Not Found!
echo Please run 'setup.bat' first.
pause
exit

:FOUND
:: 2. Activate Virtual Environment
echo [System] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 3. Run AutoTradeMachine_Eta.py
echo [System] Starting AutoTradeMachine_Eta...
python AutoTradeMachine_Eta.py

:: 4. Termination
echo [System] Program Terminated.
pause