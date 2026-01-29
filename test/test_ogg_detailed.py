#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OGG 支持调试版本
显示详细的执行信息，帮助定位问题
"""

import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)
sys.path.insert(0, current_dir)

def test_extract_audio_tags():
    """测试标签提取功能"""
    print("="*60)
    print("测试：extract_audio_tags() 函数")
    print("="*60)
    print()
    
    from supplement_album_metadata import extract_audio_tags
    
    # 创建测试文件路径（如果存在）
    test_dir = "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)"
    test_files = []
    
    # 使用 glob 查找实际的音频文件
    import glob
    if os.path.exists(test_dir):
        test_files = glob.glob(os.path.join(test_dir, "*.ogg"))[:3]  # 只测试前 3 个 OGG 文件
    
    print(f"测试目录: {test_dir}")
    print(f"找到 OGG 文件: {len(test_files)}")
    print()
    
    for test_file in test_files:
        print(f"测试文件: {os.path.basename(test_file)}")
        print("-" * 60)
        
        try:
            tags = extract_audio_tags(test_file)
            print(f"  Artist: {tags.get('artist')}")
            print(f"  Album: {tags.get('album')}")
            print(f"  Title: {tags.get('title')}")
            print(f"  返回值: {tags}")
            print("  ✅ 标签提取成功")
        except Exception as e:
            print(f"  ❌ 标签提取失败: {e}")
        
        print()

def test_embed_metadata_to_audio():
    """测试元数据嵌入功能"""
    print("="*60)
    print("测试：embed_metadata_to_audio() 函数")
    print("="*60)
    print()
    
    from supplement_album_metadata import embed_metadata_to_audio
    
    # 找一个测试文件
    test_files = glob.glob("/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)/*.ogg")
    
    if test_files:
        test_file = test_files[0]
        print(f"测试文件: {os.path.basename(test_file)}")
        print("-" * 60)
        
        try:
            # 测试只写入年份，不嵌入封面
            success = embed_metadata_to_audio(test_file, "2024", None)
            print(f"  嵌入结果: {success}")
            
            if success:
                print("  ✅ 元数据嵌入成功")
            else:
                print("  ❌ 元数据嵌入失败")
        except Exception as e:
            print(f"  ❌ 嵌入失败: {e}")
        
        print()

def test_process_album_directory():
    """测试专辑处理逻辑"""
    print("="*60)
    print("测试：process_album_directory() 函数")
    print("="*60)
    print()
    
    from supplement_album_metadata import process_album_directory
    
    test_dir = "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)"
    
    print(f"测试目录: {test_dir}")
    print()
    
    try:
        stats = process_album_directory(test_dir, api_cache=None, options={"overwrite": True})
        print(f"  总文件数: {stats.get('total', 0)}")
        print(f"  成功数: {stats.get('success', 0)}")
        print(f"  失败数: {stats.get('failed', 0)}")
        print(f"  跳过数: {stats.get('skipped', 0)}")
        print()
        
        if stats.get('success', 0) > 0:
            print("  ✅ 有文件被成功处理")
        elif stats.get('skipped', 0) > 0:
            print("  ❌ 所有文件都被跳过")
        
        print()
    except Exception as e:
        print(f"  ❌ 处理失败: {e}")
        print()

if __name__ == "__main__":
    print()
    print("OGG 支持调试测试")
    print()
    
    # 运行所有测试
    import glob
    
    # 测试 1: 标签提取
    test_extract_audio_tags()
    
    # 测试 2: 元数据嵌入
    test_embed_metadata_to_audio()
    
    # 测试 3: 专辑处理
    test_process_album_directory()
    
    print("="*60)
    print("调试测试完成")
    print("="*60)
    print()
    input("按 Enter 键退出...")
