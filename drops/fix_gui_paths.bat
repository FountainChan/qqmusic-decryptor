@echo off
echo Fixing GUI default paths...

copy "gui_backup\main_gui.py" "gui_backup\main_gui.py.bak" >nul

REM Fix input path
powershell -Command "(Get-Content 'gui_backup\main_gui.py' -Raw) -Replace 'D:\\Music\\\\VipSongsDownload', 'D:\\\\QQMusic\\Download\\\\VipSongsDownload'" | Set-Content 'gui_backup\main_gui.py' >nul

REM Fix output path
powershell -Command "(Get-Content 'gui_backup\main_gui.py' -Raw) -Replace 'D:\\\\Decrypted\\\\Music', 'D:\\\\QQMusic\\Decrypted\\\\Music'" | Set-Content 'gui_backup\main_gui.py' >nul

echo.
echo [Step 1] Verify fixes...
echo Checking input path...
findstr /C:" "gui_backup\main_gui.py" "D:\\QQMusic\\Download\\VipSongsDownload"
if errorlevel 1 echo Input path NOT fixed! & goto :error

echo Checking output path...
findstr /C:" "gui_backup\main_gui.py" "D:\\DecryptedMusic"
if errorlevel 1 echo Output path NOT fixed! & goto :error

echo.
echo All default paths have been fixed successfully!
echo.
echo [Step 2] Close old GUI
taskkill /F /IM python.exe /T 2>nul

echo [Step 3] Restart GUI
start "" "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
echo.
goto :end

:error
echo.
echo Failed to fix paths! Please manually check the file content.
echo.
pause

:end
echo.
echo Script completed. Please verify paths in GUI.
echo.
pause
