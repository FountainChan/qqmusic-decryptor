@echo off
title QQ Music 批量解密工具
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   QQ Music 批量解密工具
echo ========================================
echo.

REM 检查环境
call check_env.bat
if errorlevel 1 (
    echo.
    echo [错误] 环境检查失败，请解决上述问题
    pause
    exit /b 1
)

echo.
echo ========================================
echo   开始解密任务...
echo ========================================
echo [%date% %time%] 开始执行
echo.

REM 运行CLI解密工具
python src/main_cli.py --config "config.ini" --verbose

set RESULT=%errorlevel%

echo.
echo ========================================
if %RESULT% equ 0 (
    echo   [✓] 解密完成！
    echo   所有文件已成功转换
) else (
    echo   [⚠] 解密完成，但有部分失败
    echo   请查看日志文件：logs\decrypt.log
)
echo ========================================
echo.

pause
