@echo off
title QQ Music 解密工具 - 修复版本
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   QQ Music 解密工具
echo   修复版本 v1.1
echo ========================================
echo.

echo [1/4] 检查 frida-server...
tasklist /FI "IMAGENAME eq frida-server.exe" 2>nul | find /c "frida-server.exe" >nul
if errorlevel 1 (
    echo [!] frida-server 未运行
    echo.
    echo 请先运行: start_frida_server.bat
    echo 然后重新运行此脚本
    pause
    exit /b 1
) else (
    echo [OK] frida-server 正在运行
)

echo.
echo [2/4] 检查 QQ Music...
tasklist /FI "IMAGENAME eq QQMusic.exe" 2>nul | find /c "QQMusic.exe" >nul
if errorlevel 1 (
    echo [!] QQ Music 未运行
    echo.
    echo 正在尝试启动 QQ Music...
    start "" "D:\Software\Tencent\QQMusic\QQMusic1951.01.07.35\QQMusic.exe"
    timeout /t 10 /nobreak >nul
    tasklist /FI "IMAGENAME eq QQMusic.exe" 2>nul | find /c "QQMusic.exe" >nul
    if errorlevel 1 (
        echo [!] QQ Music 启动失败
        pause
        exit /b 1
    )
) else (
    echo [OK] QQ Music 正在运行
)

echo.
echo [3/4] 关闭旧的 GUI 窗口...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq QQ*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [4/4] 启动 GUI...
echo.
echo ========================================
echo.
echo 默认路径（已修复）:
echo   输入: G:\QQMusic\Download\VipSongsDownload
echo   输出: G:\QQMusic\Decrypted\VipSongsDownload
echo.
echo 注意: 目录结构会自动保留
echo.
echo ========================================
echo.
echo 正在启动...
echo.

cd gui_backup
start "" "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

echo.
echo ========================================
echo   GUI 已启动！
echo ========================================
echo.
echo 使用步骤:
echo   1. 在 GUI 中验证路径（如果需要，手动选择）
echo   2. 点击"开始解密"按钮
echo   3. 等待转换完成
echo.
echo ========================================
echo.
pause
