#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OGG 支持验证测试
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_imports():
    """测试导入"""
    print("="*60)
    print("测试 1: 库导入")
    print("="*60)
    print()
    
    try:
        from mutagen.flac import FLAC, Picture
        print("✅ FLAC 导入成功")
    except ImportError as e:
        print(f"❌ FLAC 导入失败: {e}")
        return False
    
    try:
        from mutagen.oggvorbis import OggVorbis
        print("✅ OGG 导入成功")
    except ImportError as e:
        print(f"❌ OGG 导入失败: {e}")
        return False
    
    print()
    return True

def test_function_existence():
    """测试函数是否存在"""
    print("="*60)
    print("测试 2: 函数存在性")
    print("="*60)
    print()
    
    try:
        from supplement_album_metadata import extract_audio_tags, embed_metadata_to_audio
        print("✅ extract_audio_tags() 函数存在")
        print("✅ embed_metadata_to_audio() 函数存在")
        print()
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except AttributeError as e:
        print(f"❌ 函数不存在: {e}")
        return False

def test_ogg_support():
    """测试 OGG 支持是否工作"""
    print("="*60)
    print("测试 3: OGG 支持功能")
    print("="*60)
    print()
    
    from supplement_album_metadata import extract_audio_tags
    
    # 创建一个临时的测试 OGG 文件（如果存在）
    test_file = "/tmp/test_ogg_support.ogg"
    
    if not os.path.exists(test_file):
        print(f"⚠️  测试文件不存在: {test_file}")
        print(f"⚠️  跳过 OGG 功能测试")
        return False
    
    # 测试标签提取
    try:
        tags = extract_audio_tags(test_file)
        print(f"✅ OGG 标签提取成功:")
        print(f"   - Artist: {tags.get('artist')}")
        print(f"   - Album: {tags.get('album')}")
        print(f"   - Title: {tags.get('title')}")
        print()
        return True
    except Exception as e:
        print(f"❌ OGG 标签提取失败: {e}")
        return False

if __name__ == "__main__":
    print()
    print("OGG 元数据支持验证测试")
    print()
    
    # 运行所有测试
    import_ok = test_imports()
    if import_ok:
        functions_ok = test_function_existence()
        if functions_ok:
            test_ogg_support()
    
    print("="*60)
    print("测试完成")
    print("="*60)
    print()
    input("按 Enter 键退出...")
