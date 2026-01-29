#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立 API 测试 - 不导入任何模块
"""

import requests
import json

API_BASE_URL = "http://192.168.110.194:3200"
albummid = "000ILKG63fED7K"

print("="*60)
print("独立 API 测试")
print("="*60)
print()

try:
    # 步骤 1：获取 API 响应
    print("步骤 1：获取 API 响应...")
    response = requests.get(
        f"{API_BASE_URL}/getAlbumInfo",
        params={"albummid": albummid},
        timeout=10
    )
    data = response.json()
    print(f"[OK] 状态码: {response.status_code}")
    print()
    
    # 步骤 2：提取数据
    print("步骤 2：提取数据...")
    response_data = data["response"]["data"]
    a_date = response_data.get("aDate")
    print(f"[OK] aDate = {a_date}")
    print(f"[OK] aDate 类型: {type(a_date)}")
    print()
    
    # 步骤 3：提取年份
    print("步骤 3：提取年份...")
    pub_year = ""
    pub_date = ""
    
    if a_date:
        a_date_str = str(a_date)
        pub_year = a_date_str[:4] if len(a_date_str) >= 4 else ""
        pub_date = a_date_str
        print(f"[OK] aDate 字符串: {a_date_str}")
        print(f"[OK] pub_year: {pub_year}")
        print(f"[OK] pub_date: {pub_date}")
    else:
        print("[FAIL] aDate 为空")
    
    print()
    print("="*60)
    print("最终结果")
    print("="*60)
    print(f"专辑名: Never Odd Or Even")
    print(f"aDate: {a_date}")
    print(f"pub_year: {pub_year}")
    print(f"pub_date: {pub_date}")
    print()
    
    if a_date:
        print("[SUCCESS] aDate 字段正确获取！")
        print(f"[SUCCESS] 年份: {pub_year}")
        print(f"[SUCCESS] 日期: {pub_date}")
    else:
        print("[FAIL] aDate 字段为空，需要检查代码")
    
except Exception as e:
    print(f"[ERROR] 异常: {e}")
    import traceback
    traceback.print_exc()
