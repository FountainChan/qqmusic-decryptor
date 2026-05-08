@echo off
title QQ Music 批量解密工具 - 依赖安装
color 0B
cd /d "%~dp0..\.."

echo ========================================
echo   QQ Music 解密工具 - 依赖安装
echo ========================================
echo.

cd /d "%~dp0..\.."

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

echo [3/3] 检查Python依赖...
python -c "import mutagen; print('OK')" >nul 2>&1 && echo [✓] mutagen已安装 || echo [警告] mutagen未安装，如需元数据处理请运行: pip install mutagen
echo.

echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步：
echo 1. 启动QQ Music客户端
echo 2. 运行: src\bat\auto_decrypt.bat 开始解密
echo.
pause
