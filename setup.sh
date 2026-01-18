#!/bin/bash

echo "[System] Starting Environment Setup..."

#[1]: Check Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 could not be found. Please install Python3."
    exit 1
fi

#[2]: Check Virtual Environment and Create
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

#[3]: Activate and Install Packages
echo "[System] Activating .venv and installing requirements..."
source .venv/bin/activate

#[4]: Upgrade PIP
pip install --upgrade pip

#[5]: Install requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo ""
    echo "-------------------------------------------------------"
    echo "[Success] Setup Completed! Now you can run './run.sh'"
else
    echo "[WARNING] requirements.txt not found."
    echo "Virtual environment is ready, but no packages were installed."
fi