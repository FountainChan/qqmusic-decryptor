@echo off
REM ============================================================
REM Album Metadata Supplement Tool - One-Click Script
REM ============================================================

chcp 65001 >nul
setlocal

REM Script directory (parent of this file)
set SCRIPT_DIR=%~dp0

REM Default input directory (modify as needed)
REM To select specific album directory, modify here directly
set DEFAULT_INPUT_DIR=G:\QQMusic\Decrypted\VipSongsDownload

REM Check if Python is available
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ============================================================
    echo   Error: Python not found
    echo ============================================================
    echo.
    echo Please ensure Python is installed and added to PATH
    echo.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Display welcome message
echo ============================================================
echo   Album Metadata Supplement Tool
echo ============================================================
echo.
echo This tool will add to FLAC files:
echo   1. Album cover (embedded in file + saved as cover.jpg)
echo   2. Release year (from API and written to DATE field)
echo.
echo Usage methods:
echo   1. Double-click this file: Use default directory
echo   2. Drag directory to this file: Process dragged directory
echo   3. Edit DEFAULT_INPUT_DIR in this file
echo.
echo ============================================================
echo.

REM Check if there are arguments (dragged to script)
set "INPUT_DIR=%~1"

if "%INPUT_DIR%"=="" (
    REM No arguments, use default directory
    set INPUT_DIR=%DEFAULT_INPUT_DIR%
    echo Using default directory: %INPUT_DIR%
    echo.
) else (
    REM Has arguments, use dragged directory
    echo Processing dragged directory: %INPUT_DIR%
    echo.
)

REM Check if directory exists
if not exist "%INPUT_DIR%" (
    echo ============================================================
    echo   Error: Directory does not exist
    echo ============================================================
    echo.
    echo Directory path: %INPUT_DIR%
    echo.
    echo Please check if the path is correct, or edit this file
    echo    to modify DEFAULT_INPUT_DIR variable
    echo.
    pause
    exit /b 1
)

REM Check if it's a file (not directory)
if exist "%INPUT_DIR%\*" (
    if not exist "%INPUT_DIR%\" (
        echo ============================================================
        echo   Error: Provided path is a file, not a directory
        echo ============================================================
        echo.
        echo Path: %INPUT_DIR%
        echo.
        echo Please provide a directory path, not a file path
        echo.
        pause
        exit /b 1
    )
)

REM Run Python script
echo Starting process...
echo.
python "%~dp0..\..\src\supplement_album_metadata.py" "%INPUT_DIR%"

REM Check execution result
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   Processing failed, error code: %errorlevel%
    echo ============================================================
    echo.
    echo Please check the error messages above
    echo.
) else (
    echo.
    echo ============================================================
    echo   Processing completed!
    echo ============================================================
    echo.
    echo Added to FLAC files:
    echo   - Album cover (embedded in file)
    echo   - Cover file (saved as cover.jpg)
    echo   - Release year (written to DATE field)
    echo.
)

echo Press any key to exit...
pause
