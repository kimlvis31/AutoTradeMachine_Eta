#!/bin/bash

# 1. 가상환경 확인
if [ ! -d ".venv" ]; then
    echo "[ERROR] Virtual Environment (.venv) Not Found!"
    echo "Please run './setup.sh' first."
    exit 1
fi

# 2. 가상환경 활성화
echo "[System] Activating virtual environment..."
source .venv/bin/activate

# 3. 메인 프로그램 실행
echo "[System] Starting AutoTradeMachine_Eta..."
echo "-------------------------------------------------------"
python3 AutoTradeMachine_Eta.py

# 4. 종료 처리
echo ""
echo "-------------------------------------------------------"
echo "[System] Program Terminated."