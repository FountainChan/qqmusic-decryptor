# 修复统计逻辑：跳过计数应该正确
# 根据用户需求：音轨号处理不计入最终成功/失败/跳过，只有年份和封面处理才计入

with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 修复统计逻辑：将 stats 初始化放在函数开头，而不是在循环内
new_stats_init = '''    # 初始化统计信息（用于最终统计）
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
    }
'''

# 在 stats 初始化之后插入 track_stats 和 final_stats
target = '''    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
'''
replacement = '''    # 初始化统计信息（用于最终统计）
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
    }
    
    stats = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "skipped": 0
    }
'''

# 替换
content = content.replace(target, replacement)

# 修改循环内的统计逻辑：音轨号处理结果计入 track_stats，不计入 final_stats
# 步骤 1：音轨号处理
old_track_success = '                stats["success"] += 1'
new_track_success = '                track_stats["track_success"] += 1'

old_track_failed = '                stats["failed"] += 1'
new_track_failed = '                track_stats["track_failed"] += 1'

old_track_skipped = '            stats["skipped"] += 1'
new_track_skipped = '            track_stats["track_skipped"] += 1'

content = content.replace(old_track_success, new_track_success)
content = content.replace(old_track_failed, new_track_failed)
content = content.replace(old_track_skipped, new_track_skipped)

# 修改步骤 2：年份和封面处理：结果计入 final_stats
# 成功
old_final_success = '                    stats["success"] += 1'
new_final_success = '                    final_stats["success"] += 1'

# 失败
old_final_failed = '                    stats["failed"] += 1'
new_final_failed = '                    final_stats["failed"] += 1'

content = content.replace(old_final_success, new_final_success)
content = content.replace(old_final_failed, new_final_failed)

# 跳过：需要添加正确的跳过计数
old_skip = '            logger.info("[SKIP] 没有年份和封面数据")'
new_skip = '''            logger.info("[SKIP] 没有年份和封面数据")
            final_stats["skipped"] += 1'''

content = content.replace(old_skip, new_skip)

# 修改最后的统计输出：使用 final_stats 而不是 stats
old_print = "print(f'总文件数: {stats.get(\"total\", 0)}')\nprint(f'成功: {stats.get(\"success\", 0)}')\nprint(f'失败: {stats.get(\"failed\", 0)}')\nprint(f'跳过: {stats.get(\"skipped\", 0)}')"
new_print = "print(f'总文件数: {final_stats.get(\"total\", 0)}')\nprint(f'成功: {final_stats.get(\"success\", 0)}')\nprint(f'失败: {final_stats.get(\"failed\", 0)}')\nprint(f'跳过: {final_stats.get(\"skipped\", 0)}')"

content = content.replace(old_print, new_print)

# 写回文件
with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("统计逻辑已修复")
