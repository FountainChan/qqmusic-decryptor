@echo off
title Quick Fix Script - Fix Default Paths
cd /d "%~dp0"

echo.
echo ========================================
echo   Fix Default Paths
echo ========================================
echo.

REM Step 1: Backup original file
copy "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py" "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py.bak"

echo.
echo [Step 1] Original file backed up
echo.

REM Step 2: Fix input path
echo [Step 2] Fix input path...
python -c "content = open(r'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py', 'r', encoding='utf-8').read(); lines = [line.replace(r'D:\\\\Music\\\\VipSongsDownload', 'G:\\\\QQMusic\\Download\\\\VipSongsDownload') for line in lines]; open(r'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py', 'w', encoding='utf-8').write(''.join(lines))"
echo [Step 2] Input path fixed
echo.

REM Step 3: Fix output path
echo [Step 3] Fix output path...
python -c "content = open(r'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py', 'r', encoding='utf-8').read(); lines = [line.replace(r'D:\\\\Decrypted\\\\Music', 'G:\\\\QQMusic\\Decrypted\\\\Music') for line in lines]; open(r'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py', 'w', encoding='utf-8').write(''.join(lines))"
echo [Step 3] Output path fixed
echo.

echo.
echo ========================================
echo   All default paths have been fixed!
echo.
echo   New paths:
echo   - Input: G:\QQMusic\Download\VipSongsDownload
echo   - Output: G:\QQMusic\Decrypted
echo.
echo ========================================
echo.
echo Step 4: Close old GUI window if running
echo Taskkill /F /IM python.exe /T 2>nul
echo.
echo Step 5: Re-run GUI
echo Start cmd /c "" "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
echo.
echo ========================================
echo.
pause
