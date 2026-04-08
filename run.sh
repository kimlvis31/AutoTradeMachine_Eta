#!/bin/bash

cleanup_memory() {
    echo ""
    echo "[System] Emergency / Normal Exit Detected."
    echo "[System] Cleaning up shared memory..."
    rm -f /dev/shm/*ATMETA_PROGRAMID*
    echo "[System] Memory cleared safely."
}
trap cleanup_memory EXIT SIGHUP SIGINT SIGTERM

# 1. Check Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[ERROR] Virtual Environment (.venv) Not Found!"
    echo "Please run './setup.sh' first."
    exit 1
fi

# 2. Activate Virtual Environment
echo "[System] Activating virtual environment..."
source .venv/bin/activate

# 3. Force X11 GUI Backend (Prevents Ubuntu Wayland Display Compatibility Crash)
export QT_QPA_PLATFORM=xcb

# 4. Run main.py
echo "[System] Starting AutoTradeMachine_Eta..."
python3 main.py

# 5. End of Script
echo ""
echo "----------------------------------------------------"
echo "[System] Program Terminated. Press Enter Key To Exit."
read
