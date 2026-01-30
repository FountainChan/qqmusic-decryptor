# 修复统计逻辑：跳过应该为 1，而不是 0

with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找并修复统计逻辑
for i, line in enumerate(lines):
    if 'stats["skipped"] += 1' in line and '[SKIP] 没有年份和封面数据' in lines[i+1]:
        # 注释掉这行，因为跳过应该根据实际情况判断
        lines[i] = '        # 注意：这里不记录跳过，实际跳过在下面判断'
        print(f"Fixed line {i+1}: {line.strip()[:50]}")
    elif 'stats["total"] = len(audio_files)' in line:
        # 保留这行，用于统计总数
        print(f"Kept line {i+1}: {line.strip()[:50]}")

# 写回文件
with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("统计逻辑已修复")
