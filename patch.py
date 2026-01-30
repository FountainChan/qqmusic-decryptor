# 创建修复补丁
import re

with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复第 756-757 行
old_pattern = r"(\s+)logger\.warning\(f\"未找到专辑: {artist} - \{album}\"\")\n(\s+)stats\[\"skipped\"\] = len\(audio_files\)\n(\s+)return stats"
new_code = r"\1logger.warning(f\"未找到专辑: {artist} - {album}\")\n\1# 注意：这里不返回，继续处理音轨号\n    \1# 不返回，继续处理文件（音轨号仍然会写入）"

content = re.sub(old_pattern, new_code, content)

with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("补丁已应用")
