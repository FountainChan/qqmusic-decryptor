@echo off
title Ultra Simple Fix
color 0E
cd /d "%~dp0"

echo ========================================
echo   超级简单修复脚本
echo ========================================
echo.

REM 方法：直接使用reg add命令修改默认值
echo.
echo [选项1] 修复输入目录
reg add "HKCU\Software\qqmusic_decryptor\gui" /v "InputPath" /t REG_SZ "G:\QQMusic\Download" /f
echo.
echo [选项2] 修复输出目录  
reg add "HKCU\Software\qqmusic_decryptor\gui" /v "OutputPath" /t REG_SZ "D:\QQMusic\Decrypted" /f
echo.
echo ========================================
echo.

echo 执行修复...
reg add "HKCU\Software\qqmusic_decryptor\gui" /v "InputPath" /t REG_SZ "G:\QQMusic\Download" /f /d "G:\QQMusic\Download" 2>nul
if errorlevel 1 echo [FAIL] 输入目录修复失败 & goto :end

reg add "HKCU\Software\qqmusic_decryptor\gui" /v "OutputPath" /t REG_SZ "D:\QQMusic\Decrypted" /f /d "G:\QQMusic\Decrypted" 2>nul
if errorlevel 1 echo [FAIL] 输出目录修复失败 & goto :end

echo [SUCCESS] 所有默认路径已修复!
echo.
echo ========================================
echo.
echo 修复内容：
echo   1. 输入目录: G:\QQMusic\Download\VipSongsDownload
echo   2. 输出目录: D:\QQMusic\Decrypted
echo.
echo ========================================
echo.
echo 重新运行GUI...
echo   关闭当前GUI窗口（如果有的话）
echo   然后运行: python "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
echo.
echo ========================================
echo.
pause
:end
