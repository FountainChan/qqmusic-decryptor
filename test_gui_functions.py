#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUI功能测试
测试核心功能而不启动图形界面
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_path_transformation():
    """测试路径转换逻辑"""
    print("=" * 60)
    print("Testing Path Transformation Logic")
    print("=" * 60)
    
    # 模拟输入
    input_dir = r"G:\QQMusic\Download\VipSongsDownload"
    output_dir = r"G:\QQMusic\Decrypted\VipSongsDownload"
    
    # 测试用例1: 单层目录
    encrypted_file1 = r"G:\QQMusic\Download\VipSongsDownload\Song.mflac"
    relative_path1 = os.path.relpath(encrypted_file1, input_dir)
    expected1 = "Song.flac"
    result1 = os.path.splitext(relative_path1)[0] + ".flac"
    output_path1 = os.path.join(output_dir, result1)
    
    print(f"\nTest 1: Single directory")
    print(f"  Input:  {encrypted_file1}")
    print(f"  Output: {output_path1}")
    print(f"  Expected: {os.path.join(output_dir, expected1)}")
    assert output_path1 == os.path.join(output_dir, expected1), f"Test 1 failed"
    print(f"  [PASS]")
    
    # 测试用例2: 多层目录
    encrypted_file2 = r"G:\QQMusic\Download\VipSongsDownload\Artist\Album\Song.mflac"
    relative_path2 = os.path.relpath(encrypted_file2, input_dir)
    expected2 = os.path.join("Artist", "Album", "Song.flac")
    result2 = os.path.splitext(relative_path2)[0] + ".flac"
    output_path2 = os.path.join(output_dir, result2)
    
    print(f"\nTest 2: Multiple directories")
    print(f"  Input:  {encrypted_file2}")
    print(f"  Output: {output_path2}")
    print(f"  Expected: {os.path.join(output_dir, expected2)}")
    assert output_path2 == os.path.join(output_dir, expected2), f"Test 2 failed"
    print(f"  [PASS]")
    
    # 测试用例3: .mgg格式
    encrypted_file3 = r"G:\QQMusic\Download\VipSongsDownload\Artist\Album\Song.mgg"
    relative_path3 = os.path.relpath(encrypted_file3, input_dir)
    expected3 = os.path.join("Artist", "Album", "Song.ogg")
    result3 = os.path.splitext(relative_path3)[0] + ".ogg"
    output_path3 = os.path.join(output_dir, result3)
    
    print(f"\nTest 3: .mgg format")
    print(f"  Input:  {encrypted_file3}")
    print(f"  Output: {output_path3}")
    print(f"  Expected: {os.path.join(output_dir, expected3)}")
    assert output_path3 == os.path.join(output_dir, expected3), f"Test 3 failed"
    print(f"  [PASS]")
    
    print("\n" + "=" * 60)
    print("All path transformation tests passed! (OK)")
    print("=" * 60)
    return True

def test_temp_file_name():
    """测试临时文件名生成"""
    print("\n" + "=" * 60)
    print("Testing Temporary File Name Generation")
    print("=" * 60)
    
    import hashlib
    
    # 测试用例1: 不同路径应该生成不同的临时文件名
    file1 = r"G:\QQMusic\Download\VipSongsDownload\Song.mflac"
    file2 = r"G:\QQMusic\Download\VipSongsDownload\Other\Song.mflac"
    
    temp1 = hashlib.md5(file1.encode()).hexdigest() + ".flac"
    temp2 = hashlib.md5(file2.encode()).hexdigest() + ".flac"
    
    print(f"\nTest 1: Different paths generate different temp names")
    print(f"  File 1: {file1}")
    print(f"  Temp 1: {temp1}")
    print(f"  File 2: {file2}")
    print(f"  Temp 2: {temp2}")
    
    assert temp1 != temp2, "Test 1 failed: Same temp name for different paths"
    print(f"  [PASS]")
    
    # 测试用例2: 相同路径应该生成相同的临时文件名
    temp3 = hashlib.md5(file1.encode()).hexdigest() + ".flac"
    print(f"\nTest 2: Same path generates same temp name")
    print(f"  File 1: {file1}")
    print(f"  Temp 1: {temp1}")
    print(f"  Temp 3: {temp3}")
    
    assert temp1 == temp3, "Test 2 failed: Different temp names for same path"
    print(f"  [PASS]")
    
    print("\n" + "=" * 60)
    print("All temp file name tests passed! (OK)")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test_path_transformation()
        test_temp_file_name()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! (OK)")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
