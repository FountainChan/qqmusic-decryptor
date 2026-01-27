#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUI 路径配置检查脚本
"""

import re
import os

gui_file = r'D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py'

# 读取文件
with open(gui_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找输入和输出路径配置
pattern = r'self\.(input_path|output_path)\.set\([\\\"](.+?)[\\\"]\)'

matches = re.findall(pattern, content)

print('='*60)
print('GUI 当前配置检查')
print('='*60)
print()

for match in matches:
    path_type = match[0]
    path_value = match[1]

    # 转换路径显示
    display_path = path_value.replace('\\\\', '\\')

    print(f'{path_type.upper()}:')
    print(f'  代码: self.{path_type}.set("{path_value}")')
    print(f'  路径: {display_path}')
    print()

print('='*60)
print('检查结果:')
print('='*60)
print()

if len(matches) >= 2:
    input_path = matches[0][1].replace('\\\\', '\\')
    output_path = matches[1][1].replace('\\\\', '\\')

    expected_input = 'G:\\QQMusic\\Download\\VipSongsDownload'
    expected_output = 'G:\\QQMusic\\Decrypted\\VipSongsDownload'

    all_correct = True

    if input_path == expected_input:
        print('[OK] 输入目录配置正确')
        print(f'      {input_path}')
    else:
        print('[FAIL] 输入目录不匹配')
        print(f'      当前: {input_path}')
        print(f'      期望: {expected_input}')
        all_correct = False

    print()

    if output_path == expected_output:
        print('[OK] 输出目录配置正确')
        print(f'      {output_path}')
    else:
        print('[FAIL] 输出目录不匹配')
        print(f'      当前: {output_path}')
        print(f'      期望: {expected_output}')
        all_correct = False

    print()
    print('='*60)
    if all_correct:
        print('所有路径配置正确！无需修改。')
    else:
        print('路径配置不正确，需要修复。')
    print('='*60)
else:
    print('[FAIL] 未找到路径配置')
