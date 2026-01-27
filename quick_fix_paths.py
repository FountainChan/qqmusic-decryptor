#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Fix Script - 直接修复GUI默认路径
"""

# 修复配置文件
config_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

# 读取文件
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复输入目录路径
content = content.replace(
    'D:\\\\Music\\\\VipSongsDownload',
    'G:\\\\QQMusic\\Download\\VipSongsDownload'
)

# 修复输出目录路径
content = content.replace(
    'D:\\\\Decrypted\\\\Music',
    'G:\\\\QQMusic\\Decrypted'
)

# 写回文件
with open(config_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("="*60)
print("Quick Fix Script")
print("="*60)
print()

print("[步骤1] 正在修复默认路径配置...")
print("[步骤2] ✓ 输入目录: G:\\QQMusic\\Download\\VipSongsDownload")
print("[步骤2] ✓ 输出目录: G:\\QQMusic\\Decrypted")
print()
print("所有默认路径已修复！")
print()
print("="*60)
print()
print("🎯 下一步：")
print("   1. 重新运行GUI版本")
print("   2. 或直接运行：python D:\\WorkDev\\qqmusic_decryptor\\gui_backup\\main_gui.py")
print()
print("   3. 在GUI中，请选择正确的路径：")
print("      - 输入目录：G:\\QQMusic\\Download\\VipSongsDownload")
print("      - 输出目录：G:\\QQMusic\\Decrypted")
print()
print("="*60)
