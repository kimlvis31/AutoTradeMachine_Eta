#!/bin/bash

# 1. Check Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[ERROR] Virtual Environment (.venv) Not Found!"
    echo "Please run './setup.sh' first."
    exit 1
fi

# 2. Activate Virtual Environment
echo "[System] Activating virtual environment..."
source .venv/bin/activate

# 3. Run AutoTradeMachine_Eta.py
echo "[System] Starting AutoTradeMachine_Eta..."
python3 AutoTradeMachine_Eta.py