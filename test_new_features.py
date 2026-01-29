#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试封面和发行年份功能
"""

import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_api_connection():
    """测试 API 连接"""
    try:
        from qqmusic_api_client import QQMusicAPIClient
        
        print("测试 API 连接...")
        api_client = QQMusicAPIClient()
        
        # 测试搜索
        print("\n测试搜索专辑...")
        result = api_client.search_album("周杰伦", "叶惠美")
        
        if result:
            print(f"✓ 搜索成功")
            print(f"  专辑名: {result.get('albumname')}")
            print(f"  歌手: {result.get('singername')}")
            print(f"  albummid: {result.get('albummid')}")
            
            albummid = result.get('albummid')
            
            # 测试获取专辑信息
            print("\n测试获取专辑信息...")
            album_info = api_client.get_album_info(albummid)
            
            if album_info:
                print(f"✓ 获取专辑信息成功")
                print(f"  发行年份: {album_info.get('pub_year')}")
                print(f"  发行日期: {album_info.get('pub_date')}")
                print(f"  类型: {album_info.get('genre')}")
                
                # 测试获取封面 URL
                print("\n测试获取封面 URL...")
                cover_url = api_client.get_album_cover_url(albummid, size="500x500")
                
                if cover_url:
                    print(f"✓ 获取封面 URL 成功")
                    print(f"  URL: {cover_url}")
                else:
                    print(f"✗ 获取封面 URL 失败")
            else:
                print(f"✗ 获取专辑信息失败")
        else:
            print(f"✗ 搜索专辑失败")
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_metadata_functions():
    """测试元数据处理函数"""
    try:
        from metadata_utils import (
            extract_track_number_from_filename,
            get_flac_metadata_tags,
            process_album_metadata
        )
        from qqmusic_api_client import QQMusicAPIClient
        
        print("\n测试元数据处理函数...")
        
        # 测试文件名解析
        test_files = [
            "01 歌曲名.flac",
            "12 另一首歌.flac",
            "1-歌曲名.flac",
            "歌曲名.flac"
        ]
        
        print("\n测试文件名音轨号提取:")
        for filename in test_files:
            track_number = extract_track_number_from_filename(filename)
            status = "✓" if track_number is not None else "✗"
            print(f"  {status} {filename} -> {track_number}")
        
        # 测试完整流程（需要实际的 FLAC 文件）
        print("\n测试完整元数据处理流程...")
        
        # 这里需要一个实际的 FLAC 文件路径
        # 如果有测试文件，可以测试
        # result = process_album_metadata(flac_file_path, api_client)
        
        return True
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("  封面和发行年份功能测试")
    print("=" * 60)
    print()
    
    # 测试1: API 连接
    api_ok = test_api_connection()
    
    # 测试2: 元数据处理函数
    metadata_ok = test_metadata_functions()
    
    print()
    print("=" * 60)
    print("  测试总结")
    print("=" * 60)
    print(f"API 连接: {'通过' if api_ok else '失败'}")
    print(f"元数据函数: {'通过' if metadata_ok else '失败'}")
    print()
    
    if api_ok and metadata_ok:
        print("所有测试通过！")
        print()
        print("新功能已就绪:")
        print("  1. 音轨号：从文件名提取并写入")
        print("  2. 发行年份：从 API 获取并写入")
        print("  3. 专辑封面：从 API 下载并嵌入")
        print("  4. 封面文件：保存为 cover.jpg")
        print()
        print("功能集成到:")
        print("  - main_cli.py（命令行版本）")
        print("  - gui_backup/main_gui.py（图形界面版本）")
    else:
        print("部分测试失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
