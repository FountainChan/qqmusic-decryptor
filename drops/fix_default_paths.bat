@echo off
set FILE=gui_backup\main_gui.py
set OLD_INPUT=D:\Music\VipSongsDownload
set NEW_INPUT=D:\QQMusic\Download\VipSongsDownload
set OLD_OUTPUT=D:\Decrypted
set NEW_OUTPUT=D:\QQMusic\Decrypted

echo ========================================
echo   Fix Default Paths
echo ========================================
echo.

copy "%FILE%" "%FILE%.bak" >nul
if errorlevel 1 goto :end

powershell -Command "(Get-Content '%FILE%' -Raw) -Replace '%OLD_INPUT%', '%NEW_INPUT%'" | Set-Content '%FILE%' >nul
if errorlevel 1 goto :end

powershell -Command "(Get-Content '%FILE%' -Raw) -Replace '%OLD_OUTPUT%', '%NEW_OUTPUT%'" | Set-Content '%FILE%' >nul
if errorlevel 1 goto :end

echo.
echo ========================================
echo   All default paths have been fixed!
echo.
echo [Step 1] Close old GUI
taskkill /F /IM python.exe /T 2>nul
echo.

echo [Step 2] Start GUI
start "" "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
echo.

echo ========================================
echo   Next steps:
echo   1. In GUI window, verify paths:
echo      - Input directory: %NEW_INPUT%
echo      - Output directory: %NEW_OUTPUT%
echo.
echo   2. Click Start Decryption
echo.
echo ========================================
echo.
:end
pause
