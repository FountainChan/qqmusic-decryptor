#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立脚本：直接更新 supplement_album_metadata.py 的处理函数
确保所有变量名都是 audio_file，同时支持 FLAC 和 OGG 格式
"""

import os
import re

# 读取原文件
with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    original_content = f.read()

# 替换整个处理函数（从 "# 处理所有音频文件（FLAC 和 OGG）" 到 "return stats"）

new_function_code = """    # 处理所有音频文件（FLAC 和 OGG）
    audio_files = []
    for root, dirs, files in os.walk(album_dir):
        for file in files:
            # 只处理支持的音频格式
            if file.lower().endswith(('.flac', '.ogg')):
                audio_files.append(os.path.join(root, file))
    
    if not audio_files:
        logger.warning(f"目录中没有支持的音频文件（.flac/.ogg）: {album_dir}")
        return stats
    
    stats["total"] = len(audio_files)
    logger.info(f"找到 {len(audio_files)} 个音频文件")
    
    # 从第一个文件获取专辑信息
    first_audio = audio_files[0]
    tags = extract_flac_tags(first_audio)
    artist = tags.get("artist")
    album = tags.get("album")
    
    if not artist or not album:
        logger.warning(f"缺少必要的标签: {first_audio}")
        stats["skipped"] = len(audio_files)
        return stats
    
    logger.info(f"专辑信息: {artist} - {album}")
    
    # 获取专辑信息（带缓存）
    cache_key = AlbumMetadataCache.generate_key(artist, album)
    album_metadata = api_cache.get(cache_key)
    
    if not album_metadata:
        logger.info("查询 API 获取专辑信息...")
        
        # 搜索专辑
        search_result = search_album(artist, album)
        if not search_result:
            logger.warning(f"未找到专辑: {artist} - {album}")
            stats["skipped"] = len(audio_files)
            return stats
        
        albummid = search_result.get("albummid")
        if not albummid:
            logger.warning(f"未找到 albummid")
            stats["skipped"] = len(audio_files)
            return stats
        
        # 获取专辑信息（包含 aDate）
        album_info = get_album_info_with_date(albummid)
        if not album_info:
            logger.warning(f"未找到专辑信息: {albummid}")
            stats["skipped"] = len(audio_files)
            return stats
        
        # 下载封面
        cover_data = download_cover(albummid, size="500x500")
        cover_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
        
        # 构建缓存数据
        album_metadata = {
            "albummid": albummid,
            "artist": search_result.get("singername"),
            "album": search_result.get("albumname"),
            "pub_year": album_info.get("pub_year", ""),
            "pub_date": album_info.get("pub_date", ""),
            "cover_data": cover_data,
            "cover_url": cover_url
        }
        
        # 写入缓存
        api_cache.set(cache_key, album_metadata)
        logger.info(f"专辑信息已缓存")
    
    # 提取信息
    pub_year = album_metadata.get("pub_year", "")
    cover_data = album_metadata.get("cover_data")
    
    if not pub_year:
        logger.warning("未找到发行年份")
    
    if not cover_data:
        logger.warning("未找到封面")
    
    # 处理所有音频文件
    for audio_file in audio_files:
        filename = os.path.basename(audio_file)
        
        # 提取并添加音轨号
        track_number = extract_track_number_from_filename(filename)
        process_single_audio_metadata(audio_file, track_number, total_tracks=stats.get("total", 0), verbose=options.get("verbose", False))
        
        # 嵌入元数据
        filename = os.path.basename(audio_file)
        success = embed_metadata_to_flac(audio_file, pub_year, cover_data)
        
        if success:
            stats["success"] += 1
            logger.info(f"[OK] {filename}")
        else:
            stats["failed"] += 1
            logger.warning(f"[FAIL] {filename}")
    
    # 保存封面到目录
    if cover_data:
        save_cover_to_directory(album_dir, cover_data)
    
    return stats"""

# 找到处理函数的开始和结束标记
start_marker = "    def process_root_directory(root_dir, options=None):"
end_marker = "    def main():"

# 执行替换
if start_marker in original_content and end_marker in original_content:
    # 找到开始和结束位置
    start_pos = original_content.find(start_marker)
    end_pos = original_content.find(end_marker)
    
    if start_pos != -1 and end_pos != -1:
        # 构建新内容
        new_content = (
            original_content[:start_pos] +
            new_function_code +
            original_content[end_pos:]
        )
        
        # 写回文件
        with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Fixed successfully!")
        print(f"  - Scan logic: Support both .flac and .ogg")
        print(f"  - Variable names: Unified use audio_file/audio_files")
        print(f"  - Function calls: Updated parameter names")
    else:
        print("ERROR: Function markers not found")
else:
    print("❌ 找不到函数标记")
