@echo off
TITLE Finance ETL Pipeline Launcher
COLOR 0A

SET REPO_PATH=/d/PERSONAL PROJECTS/yfinance-ingestion-pipeline

echo Opening Git Bash and Executing Remote Pipeline...
"C:\Program Files\Git\bin\bash.exe" --login -i -c "cd '%REPO_PATH%' && ./run_remote_etl.sh"

pause