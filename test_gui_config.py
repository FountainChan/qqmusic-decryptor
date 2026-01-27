#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试GUI配置脚本
验证修复是否正确应用
"""

import os
import sys

def test_gui_config():
    """测试GUI配置"""
    print("=" * 60)
    print("GUI 配置测试")
    print("=" * 60)
    
    # 测试1: 检查main_gui.py是否存在
    gui_path = "gui_backup/main_gui.py"
    if not os.path.exists(gui_path):
        print(f"[FAIL] 未找到: {gui_path}")
        return False
    print(f"[PASS] 文件存在: {gui_path}")
    
    # 测试2: 检查输出路径配置
    with open(gui_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    expected_output = "self.output_path.set(\"G:\\\\QQMusic\\\\Decrypted\\\\VipSongsDownload\")"
    if expected_output in content:
        print(f"[PASS] 输出路径配置正确")
        print(f"      → {expected_output}")
    else:
        print(f"[FAIL] 输出路径配置不正确")
        # 查找实际的配置
        import re
        match = re.search(r'self\.output_path\.set\(["\'](.+?)["\']\)', content)
        if match:
            print(f"      实际配置: {match.group(0)}")
        return False
    
    # 测试3: 检查目录结构保留逻辑
    if "os.path.relpath" in content:
        print(f"[PASS] 目录结构保留逻辑存在 (os.path.relpath)")
    else:
        print(f"[FAIL] 缺少目录结构保留逻辑")
        return False
    
    # 测试4: 检查自动创建目录逻辑
    if "os.makedirs(output_dir_with_path, exist_ok=True)" in content:
        print(f"[PASS] 自动创建目录逻辑存在")
    else:
        print(f"[FAIL] 缺少自动创建目录逻辑")
        return False
    
    # 测试5: 检查临时文件名使用完整路径
    if "hashlib.md5(encrypted_file.encode()).hexdigest()" in content:
        print(f"[PASS] 临时文件名使用完整路径")
    else:
        print(f"[FAIL] 临时文件名配置不正确")
        return False
    
    print("=" * 60)
    print("All tests passed! (OK)")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_gui_config()
    sys.exit(0 if success else 1)
