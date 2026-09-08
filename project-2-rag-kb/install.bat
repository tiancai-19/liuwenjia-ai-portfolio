@echo off
cd /d "%~dp0"
echo Installing dependencies (Tsinghua mirror, may take 1-3 min)...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 60
if %errorlevel% neq 0 (
  echo [FAILED] Make sure Python is installed and "Add to PATH" was checked.
  echo Download: https://www.python.org/downloads/
) else (
  echo [DONE] Dependencies installed. Double-click run.bat to start.
)
pause
