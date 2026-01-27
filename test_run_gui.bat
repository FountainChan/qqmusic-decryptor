@echo off
cd /d "%~dp0"

echo Testing run_gui_simple.bat...
echo.

echo File encoding check:
file run_gui_simple.bat

echo.
echo Testing batch execution:
echo (Note: GUI may launch and wait for user interaction)
echo.

timeout /t 2 /nobreak >nul
echo Launching GUI now...
echo.

cmd /c run_gui_simple.bat
