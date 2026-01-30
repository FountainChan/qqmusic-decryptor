# 添加跳过计数代码

# 读取文件
with open('supplement_album_metadata.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在"年份和封面处理将被跳过"之后添加跳过计数
target = 'logger.warning("年份和封面处理将被跳过，但音轨号仍然会处理")\n            # 注意：这里不返回，继续处理音轨号'
new_code = '''logger.warning("年份和封面处理将被跳过，但音轨号仍然会处理")
            # 注意：这里不返回，继续处理音轨号
            stats["skipped"] += 1'''

content = content.replace(target, new_code)

# 写回文件
with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("跳过计数代码已添加")
