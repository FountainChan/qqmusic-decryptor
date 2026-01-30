# 分析当前统计逻辑
with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找统计相关代码
stats_lines = []
for i, line in enumerate(lines):
    if 'stats["total"]' in line or 'stats["success"]' in line or 'stats["failed"]' in line or 'stats["skipped"]' in line:
        stats_lines.append((i+1, line.strip()))

print("统计相关代码：")
for line_num, line in stats_lines[-20:]:
    print(f"Line {line_num}: {line}")
