@echo off
title Frida Server - QQ Music 解密工具
color 0E
cd /d "%~dp0"

echo ========================================
echo   Frida Server 启动脚本
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 需要管理员权限！
    echo.
    echo 请右键点击此文件，选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

echo [✓] 管理员权限确认
echo.

REM 检查frida-server是否存在
if not exist "three-party\frida-server.exe" (
    echo [错误] 未找到 three-party\frida-server.exe
    echo.
    echo 请按以下步骤下载和安装frida-server：
    echo 1. 访问: https://github.com/frida/frida/releases
    echo 2. 下载: frida-server-16.7.10-windows-x86_64.exe.xz
    echo 3. 解压后放到 three-party\ 目录
    echo 4. 重命名为: frida-server.exe
    echo.
    pause
    exit /b 1
)

echo [✓] 找到 three-party\frida-server.exe
echo.
echo 启动 frida-server...
echo.
echo ========================================
echo   重要提示：
echo   1. 请不要关闭此窗口！
echo   2. 此窗口必须保持打开状态！
echo   3. 完成解密后可以关闭
echo ========================================
echo.

start /wait three-party\frida-server.exe

echo.
echo Frida Server 已停止
pause
