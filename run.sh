#!/bin/bash
# Usage: ./run.sh Train_Model.py

if [ -z "$1" ]; then
    echo "Usage: ./run.sh <script_name.py>"
    exit 1
fi

sudo ./.venv/bin/python3 "$1"
