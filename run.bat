@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

:: ClipForge Runner
:: Easy way to run the application

echo ========================================
echo  ClipForge - Video Trimmer
echo ========================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo ERROR: Python is not installed or not on PATH.
  echo Please install Python 3.8+ and ensure it's added to your system PATH.
  pause
  exit /b 1
)

:: Check if requirements are installed
echo Checking dependencies...
python -c "import moviepy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Dependencies not found. Installing requirements...
  python -m pip install -r requirements.txt --quiet
  if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
  )
  echo Dependencies installed successfully.
  echo.
)

:: Run the application
echo Starting ClipForge...
echo.
python app.py

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo Application exited with an error.
  pause
  exit /b 1
)

