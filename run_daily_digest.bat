@echo off
REM Daily AI News Digest Runner
REM This script runs the AI news aggregator pipeline

echo ========================================
echo AI News Aggregator - Daily Run
echo Started at %date% %time%
echo ========================================

REM Change to the project directory
cd /d "C:\ai news aggregator"

REM Activate virtual environment if you have one (optional)
REM call venv\Scripts\activate

REM Run the pipeline
python scripts\run_pipeline.py 24 10

echo ========================================
echo Completed at %date% %time%
echo ========================================

REM Keep window open for 5 seconds to see results
timeout /t 5
