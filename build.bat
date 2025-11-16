@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo   ClipForge - Build Script
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not on PATH.
    pause
    exit /b 1
)

REM Install/upgrade PyInstaller
echo Installing PyInstaller...
python -m pip install --upgrade --quiet "pyinstaller>=6.0.0"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Check for icon file
set ICON_FILE=
if exist "icon.ico" (
    set ICON_FILE=icon.ico
    echo Found icon: icon.ico
) else if exist "assets\clipforge.ico" (
    set ICON_FILE=assets\clipforge.ico
    echo Found icon: assets\clipforge.ico
)

REM Build using spec file
echo.
echo Building executable...
if exist ClipForge.spec (
    pyinstaller --clean --noconfirm ClipForge.spec
) else (
    echo ERROR: ClipForge.spec not found.
    pause
    exit /b 1
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Copy icon to dist folder for installer
if exist "icon.ico" (
    if not exist "dist\ClipForge" mkdir "dist\ClipForge"
    copy "icon.ico" "dist\ClipForge\" >nul 2>&1
)

echo.
echo ========================================
echo   Build completed successfully!
echo ========================================
echo.
echo Output: %CD%\dist\ClipForge\ClipForge.exe
echo.
echo To create installer, compile ClipForge.iss with Inno Setup
echo.
pause
