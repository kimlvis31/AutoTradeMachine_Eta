@echo off
title ATM Eta Launcher

:: 1. 가상환경 확인 (괄호 없이 GOTO문 사용)
if exist .venv goto FOUND
echo [ERROR] Virtual Environment (.venv) Not Found!
echo Please run 'setup.bat' first.
pause
exit

:FOUND
:: 2. 가상환경 활성화
echo [System] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 3. 메인 프로그램 실행
echo [System] Starting AutoTradeMachine_Eta...
echo -------------------------------------------------------
python AutoTradeMachine_Eta.py

:: 4. 종료 처리
echo.
echo -------------------------------------------------------
echo [System] Program Terminated.
pause