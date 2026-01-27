@echo off
title 修复默认路径配置
cd /d "%~dp0"
echo.
echo ========================================
echo   修复默认路径
echo ========================================
echo.

REM 备份原始文件
copy "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py" "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py.bak" >nul

echo [步骤1] 修改输入目录默认值...
echo 原值: D:\\Music\\VipSongsDownload
echo 新值: D:\\QQMusic\\Download\\VipSongsDownload

powershell -Command "(Get-Content 'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py' -Raw) -replace 'D:\\\\Music\\\\VipSongsDownload', 'D:\\\\QQMusic\\Download\\\\VipSongsDownload'" | Set-Content 'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py'"

echo [✓] 输入目录路径已修复
echo.

echo [步骤2] 修改输出目录默认值...
echo 原值: D:\\DecryptedMusic
echo 新值: D:\\QQMusic\\Decrypted

powershell -Command "(Get-Content 'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py' -Raw) -replace 'D:\\\\DecryptedMusic', 'D:\\\\QQMusic\\Decrypted\\\\Music'" | Set-Content 'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py'"

echo [✓] 输出目录路径已修复
echo.

echo ========================================
echo   所有默认路径已修复！
echo.
echo 现在您需要：
echo   1. 关闭当前运行的GUI窗口（如果有的话）
echo   2. 重新运行GUI版本
echo.
echo   修复后，请选择正确的路径：
echo   - 输入目录: G:\QQMusic\Download\VipSongsDownload
echo   - 输出目录: G:\QQMusic\Decrypted
echo.
echo ========================================
echo.
pause
