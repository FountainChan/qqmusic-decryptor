@echo off
cd /d "%~dp0"

python src/gui/main_gui.py
if errorlevel 1 (
    echo.
    echo 发生错误，按任意键退出...
    pause >nul
)
