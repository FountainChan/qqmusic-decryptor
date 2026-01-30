# 重新实现统计逻辑
with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并替换整个统计处理部分
old_stats = '''    # 初始化统计信息（用于最终统计）
    track_stats = {
        "track_success": 0,
        "track_failed": 0,
        "track_skipped": 0
    }
    final_stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }'''

new_stats = '''    # 初始化统计信息
    final_stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }'''

content = content.replace(old_stats, new_stats)

# 替换音轨号统计部分：移除 track_stats，不记录到 final_stats
old_track_stats = '''        # 步骤 1：音轨号处理（不依赖 API，总是尝试）
        track_number = extract_track_number_from_filename(filename)
        if track_number is not None:
            # 写入音轨号（不依赖 API）
            success = write_track_number(audio_file, track_number)
            if success:
                track_stats["track_success"] += 1
                logger.info(f"[OK] 音轨号: {track_number}")
            else:
                track_stats["track_failed"] += 1
                logger.warning(f"[FAIL] 音轨号: {track_number}")
        else:
            logger.warning("[SKIP] 未找到音轨号")
            track_stats["track_skipped"] += 1'''

new_track_stats = '''        # 步骤 1：音轨号处理（不依赖 API，总是尝试）
        track_number = extract_track_number_from_filename(filename)
        if track_number is not None:
            # 写入音轨号（不依赖 API）
            success = write_track_number(audio_file, track_number)
            if success:
                logger.info(f"[OK] 音轨号: {track_number}")
            else:
                logger.warning(f"[FAIL] 音轨号: {track_number}")
        else:
            logger.warning("[SKIP] 未找到音轨号")'''

content = content.replace(old_track_stats, new_track_stats)

# 替换年份和封面统计部分：将跳过计数移动到 else 分支
old_metadata_stats = '''        # 步骤 2：年份和封面处理（依赖 API，可能为 None）
        if pub_year or cover_data:
            try:
                success = embed_year_and_cover(audio_file, pub_year, cover_data)
                if success:
                    stats["success"] += 1
                    logger.info(f"[OK] {filename}")
                else:
                    stats["failed"] += 1
                    logger.warning(f"[FAIL] {filename}")
            except Exception as e:
                logger.error(f"嵌入年份和封面失败 {filename}: {e}")
                stats["failed"] += 1
        else:
            logger.info("[SKIP] 没有年份和封面数据")'''

new_metadata_stats = '''        # 步骤 2：年份和封面处理（依赖 API，可能为 None）
        if pub_year or cover_data:
            try:
                success = embed_year_and_cover(audio_file, pub_year, cover_data)
                if success:
                    final_stats["success"] += 1
                    logger.info(f"[OK] {filename}")
                else:
                    final_stats["failed"] += 1
                    logger.warning(f"[FAIL] {filename}")
            except Exception as e:
                logger.error(f"嵌入年份和封面失败 {filename}: {e}")
                final_stats["failed"] += 1
        else:
            logger.info("[SKIP] 没有年份和封面数据")
            final_stats["skipped"] += 1'''

content = content.replace(old_metadata_stats, new_metadata_stats)

# 替换 stats 使用为 final_stats
old_stats_usage = '''        stats["total"] += 1'''
new_stats_usage = '''        final_stats["total"] += 1'''

content = content.replace(old_stats_usage, new_stats_usage)

# 写回文件
with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("统计逻辑已重写")
