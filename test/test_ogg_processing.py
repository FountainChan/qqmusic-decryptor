#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立测试：验证 OGG 处理
不依赖有问题的 process_album_directory() 函数
"""

import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_ogg_processing():
    """测试 OGG 文件处理"""
    print("="*60)
    print("独立测试：OGG 文件处理")
    print("="*60)
    print()
    
    # 测试目录
    test_dir = "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)"
    
    print(f"测试目录: {test_dir}")
    print()
    
    # 查找音频文件
    flac_files = glob.glob(os.path.join(test_dir, "*.flac"))
    ogg_files = glob.glob(os.path.join(test_dir, "*.ogg"))
    
    print(f"FLAC 文件数: {len(flac_files)}")
    print(f"OGG 文件数: {len(ogg_files)}")
    print(f"总音频文件数: {len(flac_files) + len(ogg_files)}")
    print()
    
    # 测试前 3 个 OGG 文件
    if ogg_files:
        print("测试前 3 个 OGG 文件:")
        print("-" * 60)
        
        for i, ogg_file in enumerate(ogg_files[:3]):
            filename = os.path.basename(ogg_file)
            print(f"{i+1}. {filename}")
            print()
            
            # 测试标签提取
            try:
                from supplement_album_metadata import extract_audio_tags
                tags = extract_audio_tags(ogg_file)
                
                artist = tags.get("artist")
                album = tags.get("album")
                title = tags.get("title")
                
                print(f"   Artist: {artist}")
                print(f"   Album: {album}")
                print(f"   Title: {title}")
                print()
                
                if artist and album:
                    print(f"   ✓ 标签提取成功")
                else:
                    print(f"   ✗ 标签缺失")
                    print(f"   Artist: {artist}")
                    print(f"   Album: {album}")
                    print(f"   Title: {title}")
                print()
                
            except Exception as e:
                print(f"   ✗ 标签提取失败: {e}")
                print()
        
        print("="*60)
        print("测试完成")
        print("="*60)
    else:
        print("未找到 OGG 文件")

if __name__ == "__main__":
    test_ogg_processing()
    print()
    input("按 Enter 键退出...")
