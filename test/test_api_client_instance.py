#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 QQMusicAPIClient 实例
"""

# 导入
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qqmusic_api_client import QQMusicAPIClient

# 创建实例
api = QQMusicAPIClient()
print(f"base_url: {api.base_url}")
print(f"timeout: {api.timeout}")
print()

# 测试
albummid = "000ILKG63fED7K"

print("测试 get_album_info_with_date:")
result = api.get_album_info_with_date(albummid)
if result:
    print(f"  albumname: {result.get('albumname')}")
    print(f"  aDate: {result.get('aDate')}")
    print(f"  pub_year: {result.get('pub_year')}")
    print(f"  pub_date: {result.get('pub_date')}")
else:
    print("  获取失败")
