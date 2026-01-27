@echo off
title 修复GUI默认路径和目录结构
echo.
echo ========================================
echo   修复两个关键问题
echo ========================================
echo.
echo [问题1] 修复输出目录默认值
echo   原值: D:\DecryptedMusic
echo   新值: G:\QQMusic\Decrypted\VipSongsDownload
echo.

cd /d "%~dp0gui_backup"

REM 修复输出目录默认值（第99行）
powershell -Command "(Get-Content 'main_gui.py' -Raw) -replace 'D:\\\\Decrypted\\\\Music', 'G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload' | Set-Content 'main_gui.py'"
echo [✓] 输出目录路径已修复
echo.

REM 备份原始文件
copy "main_gui.py" "main_gui.py.bak" >nul

REM 修复目录结构问题（第55行附近）
echo [问题2] 修复目录结构保留逻辑
echo.

echo 正在应用补丁...
REM 使用Python直接修改文件，因为PowerShell替换有编码问题
python -c "
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 读取文件
with open('gui_backup/main_gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复第55行附近的代码
# 原代码: output_file = os.path.splitext(file_name)[0] + output_ext
# 新代码: output_file = os.path.join(input_dir, os.path.relpath(encrypted_file, input_dir)).replace(os.path.splitext(file_name)[0] + '.mflac', os.path.splitext(file_name)[0] + output_ext)

# 实际上更简单的修复是在第56行
# 将 output_file_path = os.path.join(output_dir, output_file)
# 改为: output_file_path = os.path.join(output_dir, os.path.relpath(encrypted_file, input_dir))

# 但更简单的方法是：保留加密文件的完整路径结构
# 在第56行之前添加一行来计算相对路径

# 实际最简单的方法：
# 在第56行修改为：
# output_file_path = output_file
# 并在此行之前添加：
# relative_path = os.path.relpath(encrypted_file, input_dir)
# output_file = os.path.join(relative_path.replace('.mflac', '').replace('.mgg', '') + output_ext)

# 然后将第56行改为：
# output_file_path = os.path.join(output_dir, relative_path)

# 让我们直接修复
new_lines = []
for i, line in enumerate(lines):
    if 'output_file_path = os.path.join(output_dir, output_file)' in line:
        # 在这一行之前添加相对路径计算
        new_lines.append('                # 计算相对路径以保留目录结构\n')
        new_lines.append('                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
        new_lines.append('                output_file_path = os.path.join(output_dir, relative_path)\n')
        # 修改这一行为注释
        new_lines.append('                # output_file_path = os.path.join(output_dir, output_file)  # 旧代码\n')
    else:
        new_lines.append(line)

# 写回文件
with open('gui_backup/main_gui.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✓ 目录结构保留逻辑已修复')
"

if errorlevel 1 (
    echo [✗] 修复失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   修复完成！
echo.
echo 修复内容：
echo   1. 输出目录: G:\QQMusic\Decrypted\VipSongsDownload
echo   2. 目录结构: 已修复，保留原始层级
echo.
echo ========================================
echo.
echo [下一步] 重新运行GUI
echo   请选择正确的路径：
echo   - 输入: G:\QQMusic\Download\VipSongsDownload
echo   - 输出: G:\QQMusic\Decrypted\VipSongsDownload
echo.
echo ========================================
echo.
pause
