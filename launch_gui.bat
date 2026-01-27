@echo off
title QQ Music 解密工具 - GUI版本启动器
color 0B
cd /d "%~dp0"

echo.
echo ========================================
echo   QQ Music 解密工具 - GUI版本
echo ========================================
echo.

REM 检查1：frida-server
echo [1/4] 检查 frida-server...
tasklist /FI "IMAGENAME eq frida-server.exe" 2>nul | find /c "frida-server.exe" >nul
if errorlevel 1 (
    echo [FAIL] frida-server 未运行
    echo.
    echo 请先以管理员身份运行: start_frida_server.bat
    pause
    exit /b 1
) else (
    echo [PASS] frida-server 正在运行
)

REM 检查2：QQ Music
echo [2/4] 检查 QQ Music...
tasklist /FI "IMAGENAME eq QQMusic.exe" 2>nul | find /c "QQMusic.exe" >nul
if errorlevel 1 (
    echo [FAIL] QQ Music 未运行
    echo.
    echo 请先启动 QQ Music 客户端
    echo 并确保已登录VIP账号
    pause
    exit /b 1
) else (
    echo [PASS] QQ Music 正在运行
    echo   进程信息：
    for /f "tokens=1,2,3" %%a in ('tasklist /FI "IMAGENAME eq QQMusic.exe" /FO CSV') do (
        echo     PID: %%a, 内存: %%c K, 名称: %%d
    )
)

echo.
echo ========================================
echo   系统检查完成，正在启动GUI版本...
echo ========================================
echo.

REM 检查GUI文件是否存在
if not exist "gui_backup\main_gui.py" (
    echo [FAIL] 未找到 GUI 文件: gui_backup\main_gui.py
    pause
    exit /b 1
)

REM 检查Frida脚本是否存在
if not exist "hook_qq_music.js" (
    echo [FAIL] 未找到 Frida 脚本: hook_qq_music.js
    pause
    exit /b 1
)

REM 启动GUI
echo [3/4] 启动 GUI 版本...
python gui_backup/main_gui.py

echo.
echo ========================================
echo.
echo 说明：
echo ========================================
echo.
echo   GUI 窗口已打开
echo.
echo   使用步骤：
echo     1. 点击"选择输入目录"按钮
echo     2. 浏览并选择: G:\QQMusic\Download
echo     3. 点击"选择输出目录"按钮
echo     4. 浏览并选择: G:\QQMusic\Decrypted
echo     5. 点击"开始解密"按钮
echo.
echo   等待转换完成...
echo   预计时间：15-20分钟
echo.
echo   转换完成后，文件将保存在: G:\QQMusic\Decrypted
echo ========================================
echo.
pause
