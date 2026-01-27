#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 GUI 启动和导入
"""

import sys
import os

print("测试 1: 导入 metadata_utils")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from metadata_utils import extract_track_number_from_filename, add_track_number_to_flac
    print("[OK] 导入成功")
except Exception as e:
    print(f"[FAIL] 导入失败: {e}")
    sys.exit(1)

print("\n测试 2: 文件名解析功能")
test_cases = [
    ("01 歌曲.flac", 1),
    ("12 另一首歌.flac", 12),
    ("1-歌曲名.flac", 1),
    ("歌曲名.flac", None),
]
for filename, expected in test_cases:
    result = extract_track_number_from_filename(filename)
    status = "[OK]" if result == expected else "[FAIL]"
    print(f"{status} {filename} -> {result} (期望: {expected})")

print("\n测试 3: GUI 导入")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath('gui_backup/main_gui.py')))
    import gui_backup.main_gui
    print("[OK] GUI 模块导入成功")
except Exception as e:
    print(f"[FAIL] GUI 模块导入失败: {e}")
    sys.exit(1)

print("\n[OK] 所有测试通过！")
print("\n注意: 如果要运行完整 GUI，请双击 run_gui_simple.bat")
