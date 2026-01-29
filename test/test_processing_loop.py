#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单独测试处理循环逻辑
用于诊断和验证文件处理问题
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_processing_loop():
    """测试处理循环"""
    print("="*60)
    print("测试：处理循环逻辑")
    print("="*60)
    print()
    
    # 导入必要的函数
    from supplement_album_metadata import (
        process_album_directory,
        AlbumMetadataCache
    )
    
    # 测试目录
    album_dir = "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)"
    
    print(f"测试目录: {album_dir}")
    print()
    
    # 检查目录是否存在
    if not os.path.exists(album_dir):
        print(f"ERROR: 目录不存在")
        return
    
    # 扫描文件
    import glob
    flac_files = glob.glob(os.path.join(album_dir, "*.flac"))
    ogg_files = glob.glob(os.path.join(album_dir, "*.ogg"))
    
    print(f"找到 FLAC 文件: {len(flac_files)}")
    print(f"找到 OGG 文件: {len(ogg_files)}")
    print(f"总音频文件: {len(flac_files) + len(ogg_files)}")
    print()
    
    # 合并文件列表
    audio_files = flac_files + ogg_files
    
    if not audio_files:
        print("ERROR: 没有找到任何音频文件")
        return
    
    # 显示前 5 个文件
    print("前 5 个文件:")
    for i, file in enumerate(audio_files[:5]):
        filename = os.path.basename(file)
        ext = filename.split('.')[-1]
        print(f"  {i+1}. {filename} ({ext})")
    print()
    
    # 尝试处理
    print("开始处理...")
    print()
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for i, audio_file in enumerate(audio_files):
        filename = os.path.basename(audio_file)
        ext = filename.split('.')[-1].lower()
        
        try:
            print(f"[{i+1}/{len(audio_files)}] 处理: {filename} ({ext})")
            
            # 提取标签
            from supplement_album_metadata import extract_audio_tags
            tags = extract_audio_tags(audio_file)
            
            if not tags.get("artist") or not tags.get("album"):
                print(f"  ✗ 标签缺失: Artist={tags.get('artist')}, Album={tags.get('album')}")
                skip_count += 1
                continue
            
            print(f"  ✓ 标签: Artist={tags.get('artist')}, Album={tags.get('album')}")
            
            # 只提取标签，不实际写入元数据
            print(f"  ✓ 模拟元数据嵌入（跳过实际写入）")
            success_count += 1
            print(f"  ✓ 处理成功")
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            fail_count += 1
        
        print()
    
    print("="*60)
    print("测试完成")
    print("="*60)
    print()
    print(f"总文件数: {len(audio_files)}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"跳过: {skip_count}")
    print()

if __name__ == "__main__":
    test_processing_loop()
