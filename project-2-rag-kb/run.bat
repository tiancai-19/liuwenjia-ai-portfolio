@echo off
cd /d "%~dp0"
echo Starting Enterprise RAG Knowledge Base...
echo Browser will open at http://localhost:8501
echo First time? Run install.bat first.
echo Usage: paste your Zhipu API Key on the left sidebar, then ask a question.
streamlit run app.py
pause
