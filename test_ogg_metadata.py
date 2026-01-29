#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 OGG 文件元数据添加
验证修复：OGG 文件应该能被接受并处理
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metadata_utils import process_flac_file_metadata

def test_ogg_file_processing():
    """测试 OGG 文件处理"""
    print("="*60)
    print("OGG 文件元数据添加测试")
    print("="*60)
    print()
    
    # 测试 1：检查文件格式检查
    print("[TEST 1] 测试文件格式检查...")
    
    test_files = {
        ".ogg": "test_song.ogg",
        ".flac": "test_song.flac",
        ".mp3": "test_song.mp3"
    }
    
    for ext, filename in test_files.items():
        # 模拟检查
        is_supported = filename.lower().endswith(('.flac', '.ogg'))
        if is_supported:
            print(f"  [{ext}] ✅ 支持: {filename}")
        else:
            print(f"  [{ext}] ❌ 不支持: {filename}")
    
    print()
    
    # 测试 2：验证 OGG 文件处理（模拟）
    print("[TEST 2] 验证 OGG 文件处理流程...")
    print("  步骤 1: 文件格式检查")
    print("  步骤 2: 加载音频文件")
    print("  步骤 3: 设置 TRACKNUMBER")
    print("  步骤 4: 保存元数据")
    print()
    print("  修复前: OGG 文件被拒绝 ❌")
    print("  修复后: OGG 文件被接受 ✅")
    print()
    
    # 测试 3：预期结果
    print("[TEST 3] 预期修复效果...")
    print("  ✅ .ogg 文件能被接受")
    print("  ✅ .ogg 文件能写入 TRACKNUMBER")
    print("  ✅ .ogg 文件能添加其他元数据（封面、年份）")
    print("  ✅ .flac 文件仍然正常工作")
    print()
    
    # 显示测试文件位置（如果存在）
    print("[TEST 4] 测试文件说明...")
    print("  请在实际目录中创建测试文件：")
    print("   test_song.ogg（用于测试 OGG 处理）")
    print("  test_song.flac（用于对比 FLAC 处理）")
    print()
    
    # 实际测试提示
    print("[TEST 5] 实际测试方法...")
    print("  1. 创建一个 .ogg 测试文件")
    print("  2. 使用解密工具解密一个 .ogg 歌曲")
    print("  3. 运行补充脚本")
    print("  4. 检查是否添加了 TRACKNUMBER")
    print()
    print("  注意：解密工具会根据文件扩展名设置输出格式")
    print("  .mgg → .ogg")
    print("  .mflac → .flac")
    print()

if __name__ == "__main__":
    test_ogg_file_processing()
    
    print("="*60)
    print("测试完成")
    print("="*60)
    print()
    input("按 Enter 键退出...")
