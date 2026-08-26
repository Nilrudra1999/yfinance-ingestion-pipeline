#!/usr/bin/env bash
set -e

# Ensure Git Bash can locate Windows installed binaries
export PATH=$PATH:"/c/Program Files/GitHub CLI/":"/c/Program Files/Python311/":"/c/Program Files/Python311/Scripts/"
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$PROJECT_DIR"
TICKER_FILE="tickers.txt"
if [ ! -f "$TICKER_FILE" ]; then
    echo "Error: $TICKER_FILE does not exist in $PROJECT_DIR"
    exit 1
fi

# Convert multi-line tickers.txt into a single comma-separated string
TICKERS=$(tr '\r\n' ',' < "$TICKER_FILE" | sed 's/,\+/,/g' | sed 's/^,//;s/,$//')

echo "=========================================="
echo " Starting Remote ETL Execution via GitHub"
echo " Tickers: $TICKERS"
echo "=========================================="

# Trigger GitHub Action Workflow
gh workflow run run_etl.yml -f tickers="$TICKERS"
echo "Waiting for GitHub workflow to start and finish..."
sleep 5

# Fetch latest run ID
RUN_ID=$(gh run list --workflow=run_etl.yml --limit 1 --json databaseId -q '.[0].databaseId')

# Watch execution until completion
gh run watch "$RUN_ID"
echo "Downloading extracted artifact from GitHub..."

# Clean up any existing local JSON output before downloading
rm -f transformed_data.json
gh run download "$RUN_ID" --name transformed-etl-data --dir .
echo "Loading data into Local MS SQL Express..."

# Activate local virtual environment if present
if [ -d "etl_venv" ]; then
    source etl_venv/Scripts/activate
fi
python main.py --mode local-load --input-json transformed_data.json

echo "=========================================="
echo " ETL Process Successfully Finished!"
echo "=========================================="
