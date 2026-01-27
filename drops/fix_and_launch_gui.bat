@echo off
title QQ Music 解密工具 - 修复并启动 GUI
color 0B
cd /d "%~dp0"

echo.
echo ========================================
echo   QQ Music 解密工具 - 修复并启动
echo ========================================
echo.

echo [步骤 1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] 未找到 Python
    echo.
    echo 请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        echo [OK] Python 版本: %%i
    )
)

echo.
echo [步骤 2/3] 应用 GUI 修复...
python fix_gui_complete.py
if errorlevel 1 (
    echo [FAIL] 修复失败
    pause
    exit /b 1
)

echo.
echo [步骤 3/3] 启动 GUI...
echo.
echo 请在 GUI 窗口中验证以下设置：
echo   - 输入目录: G:\QQMusic\Download\VipSongsDownload
echo   - 输出目录: G:\QQMusic\Decrypted\VipSongsDownload
echo.
echo 然后点击"开始解密"按钮
echo.
pause

REM 启动 GUI
python gui_backup/main_gui.py

echo.
echo ========================================
echo.
pause
