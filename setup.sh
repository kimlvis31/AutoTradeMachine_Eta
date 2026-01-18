#!/bin/bash

echo "[System] Starting Environment Setup..."
echo "-------------------------------------------------------"

# 1. 파이썬 확인 (python3 명령어로 확인)
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 could not be found. Please install Python3."
    exit 1
fi

# 2. 가상환경(.venv) 확인 및 생성
if [ -d ".venv" ]; then
    echo "[System] Virtual environment (.venv) already exists."
else
    echo "[System] Creating virtual environment (.venv)..."
    python3 -m venv .venv
    if [ ! -d ".venv" ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
    echo "[System] .venv created successfully."
fi

# 3. 활성화 및 패키지 설치
echo "[System] Activating .venv and installing requirements..."
source .venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# requirements.txt 설치
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo ""
    echo "-------------------------------------------------------"
    echo "[Success] Setup Completed! Now you can run './run.sh'"
else
    echo "[WARNING] requirements.txt not found."
    echo "Virtual environment is ready, but no packages were installed."
fi