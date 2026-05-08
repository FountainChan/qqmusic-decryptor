@echo off
title QQ Music 批量解密工具 - 依赖安装
color 0B
cd /d "%~dp0"

echo ========================================
echo   QQ Music 解密工具 - 依赖安装
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装，请先安装Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [✓] Python已安装
python --version
echo.

echo [2/3] 安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)
echo [✓] 依赖安装成功
echo.

echo [3/3] 检查frida-server...
if not exist "three-party\frida-server.exe" (
    echo [警告] three-party\frida-server.exe未找到
    echo.
    echo 请按以下步骤下载和安装frida-server：
    echo 1. 访问: https://github.com/frida/frida/releases
    echo 2. 下载: frida-server-16.7.10-windows-x86_64.exe.xz
    echo 3. 解压后放到 three-party\ 目录
    echo 4. 重命名为: frida-server.exe
    echo 5. 以管理员身份运行
) else (
    echo [✓] three-party\frida-server.exe已找到
)
echo.

echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 以管理员身份运行: start_frida_server.bat
echo 2. 启动QQ Music客户端
echo 3. 运行: auto_decrypt.bat 开始解密
echo.
pause
