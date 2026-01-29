@echo off
title Test Script
chcp 65001 >nul

echo [TEST 1] This is test line 1
echo [TEST 2] This is test line 2
echo [TEST 3] This is test line 3
echo.
echo [TEST 4] Python check...
where python
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)
echo [TEST 5] Python found OK
echo.
echo [TEST 6] Run Python script...
python supplement_album_metadata.py "G:\QQMusic\Decrypted\VipSongsDownload\闫泽欢"
echo.
echo [TEST 7] Script execution completed
echo.
pause
