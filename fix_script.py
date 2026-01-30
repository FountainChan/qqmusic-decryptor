import json

# 创建修复内容
fix_data = {
    "filePath": r"D:\WorkDev\qqmusic_decryptor\supplement_album_metadata.py",
    "old_string": '            logger.warning(f"未找到专辑: {artist} - {album}")\n            stats["skipped"] = len(audio_files)\n            return stats\n        \n        albummid = search_result.get("albummid")',
    "new_string": '            logger.warning(f"未找到专辑: {artist} - {album}")\n            # 注意：这里不返回，继续处理音轨号\n        \n        albummid = search_result.get("albummid") if search_result else None'
}

print(json.dumps(fix_data, ensure_ascii=False, indent=2))
