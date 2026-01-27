@echo off
title GUI 诊断工具
color 0E
cd /d "%~dp0"

echo.
echo ========================================
echo   QQ Music 解密工具 - GUI 诊断
echo ========================================
echo.
echo 此脚本将诊断GUI启动所需的环境
echo.
echo 正在启动诊断...
echo.

python diagnose_gui.py

pause
