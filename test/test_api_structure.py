#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API 响应结构追踪测试
"""

import requests
import json

API_BASE_URL = "http://192.168.110.194:3200"
albummid = "000ILKG63fED7K"

print("="*60)
print("API 响应结构追踪")
print("="*60)
print()

print("步骤 1：获取完整 API 响应")
print("-"*60)
response = requests.get(
    f"{API_BASE_URL}/getAlbumInfo",
    params={"albummid": albummid},
    timeout=10
)
data = response.json()

print(f"完整 JSON:")
print(json.dumps(data, indent=2, ensure_ascii=False))
print()

print("步骤 2：逐层访问数据")
print("-"*60)
print(f"data['response']['code'] = {data['response']['code']}")
print(f"data['response']['message'] = {data['response'].get('message')}")
print()

print("步骤 3：访问 data 层")
print("-"*60)
data_layer = data["response"]["data"]
print(f"data 层类型: {type(data_layer)}")
print(f"data 层键: {list(data_layer.keys())}")
print()

print("步骤 4：访问 aDate 字段")
print("-"*60)
a_date = data_layer.get("aDate")
print(f"aDate = {a_date}")
print(f"aDate 类型: {type(a_date)}")
print()

print("步骤 5：访问 list 层")
print("-"*60)
list_layer = data_layer.get("list", [])
print(f"list 长度: {len(list_layer)}")
print()

if list_layer:
    print("步骤 6：访问 list[0]")
    print("-"*60)
    album_info = list_layer[0]
    print(f"album_info 键: {list(album_info.keys())}")
    print(f"album_info['albumdesc'] = {album_info.get('albumdesc', '')[:50]}")
    print()

    print("步骤 7：比较两种获取方式")
    print("-"*60)
    print(f"方式1（从 data 层）: aDate = {a_date}")
    print(f"方式2（从 list[0]）: aDate = {album_info.get('aDate', 'N/A')}")
    print()

    print("="*60)
    print("结论:")
    print("="*60)
    if a_date:
        print("[OK] aDate 在 data 层，应该使用: data['response']['data']['aDate']")
    else:
        if "aDate" in album_info:
            print("[OK] aDate 在 list[0] 中，应该使用: list[0]['aDate']")
        else:
            print("[FAIL] aDate 不存在，需要从 albumdesc 中提取")
            albumdesc = album_info.get('albumdesc', '')
            if albumdesc:
                import re
                match = re.search(r'(\d{4})年', albumdesc)
                if match:
                    print(f"[OK] 从描述中提取年份: {match.group(1)}")
