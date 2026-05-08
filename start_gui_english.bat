@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo ========================================
echo QQ Music Decryptor - GUI Launcher
echo ========================================
echo.

echo [1/3] Checking Python dependencies...
python -c "import frida; print('OK')" >nul 2>&1
if errorlevel 1 (
    echo [FAIL] frida not installed, run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
) else (
    echo [PASS] frida is installed
)

echo [2/3] Checking QQ Music...
tasklist /FI "IMAGENAME eq QQMusic.exe" 2>nul | find /c "QQMusic.exe" >nul
if errorlevel 1 (
    echo [FAIL] QQ Music not running
    echo.
    echo Please start QQ Music client and login with VIP account
    echo.
    pause
    exit /b 1
) else (
    echo [PASS] QQ Music is running
)

echo.
echo [3/3] Starting GUI...
echo.

if not exist "src\gui\main_gui.py" (
    echo [FAIL] GUI file not found: src\gui\main_gui.py
    echo.
    pause
    exit /b 1
)

echo Command: pythonw src\gui\main_gui.py
start pythonw src\gui\main_gui.py

echo.
echo [SUCCESS] GUI window opened!
echo.
echo ========================================
echo Usage Guide
echo ========================================
echo.
echo GUI window is opened in new window
echo.
echo Default Config:
echo   - Input: G:\QQMusic\Download\VipSongsDownload
echo   - Output: G:\QQMusic\Decrypted\VipSongsDownload
echo.
echo Steps:
echo   1. Check input/output directories
echo   2. Click "Start Decrypt" button
echo   3. Wait for conversion to complete
echo.
echo If GUI window not opened, please check:
echo   1. Python installation
echo   2. Frida package (version 16.7.10)
echo   3. tkinter library
echo.
echo Press any key to close this window...
pause >nul
