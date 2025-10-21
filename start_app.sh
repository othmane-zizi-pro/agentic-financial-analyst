#!/bin/bash
set -e

echo "=== Databricks App Startup ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Git commit: $(git rev-parse HEAD 2>/dev/null || echo 'Not in git repo')"

echo ""
echo "=== Installing dependencies ==="
pip install -q pandas gradio requests

echo ""
echo "=== Checking for yfinance import in code ==="
if grep -q "import yfinance" financial_app_clean.py 2>/dev/null; then
    echo "ERROR: financial_app_clean.py still imports yfinance!"
    exit 1
fi

echo "✓ No yfinance imports found in financial_app_clean.py"

echo ""
echo "=== Starting Financial Analyst App ==="
echo "Using direct Yahoo Finance API (no yfinance dependency)"
echo "Server will start on 0.0.0.0:8000"
echo ""

python financial_app_clean.py
