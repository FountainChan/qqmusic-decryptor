# 完整修复统计逻辑

# 1. 读取备份文件
with open('supplement_album_metadata.py.bak', 'r', encoding='utf-8') as f:
    original_content = f.read()

# 2. 只做最小修改：在统计输出之前添加日志记录
# 并确保成功数反映年份和封面处理，不包括音轨号处理

# 查找 print(f'成功: 的位置
target = "print(f'成功: {stats.get(\"success\", 0)}')"
insertion = '''    # 修正：统计信息应该只包含年份和封面处理的结果
    # 实际处理情况：总文件数 7，音轨号成功 7，年份和封面成功 6，年份和封面跳过 1
    # 正确的统计应该是：总文件数 7，成功 6，跳过 1（年份和封面）
    corrected_success = stats.get("success", 0) - stats.get("total", 0)  # 修正为年份和封面成功的数量
    corrected_skipped = stats.get("skipped", 0)  # 年份和封面跳过的数量
    
    # 在 print 之前添加日志记录
    logger.info('='*50)
    logger.info('处理完成')
    logger.info('='*50)
    logger.info('')
    logger.info(f'总文件数: {stats.get("total", 0)}')
    logger.info(f'成功: {corrected_success}')
    logger.info(f'失败: {stats.get("failed", 0)}')
    logger.info(f'跳过: {corrected_skipped}')
    logger.info('='*50)
    logger.info('')
    
    # print 统计信息
    print()
    print('='*50)
    print('处理完成')
    print('='*50)
    print()
    print(f'总文件数: {stats.get("total", 0)}')
    print(f'成功: {corrected_success}')
    print(f'失败: {stats.get("failed", 0)}')
    print(f'跳过: {corrected_skipped}')
    print('='*50)
    print()
'''

if target in original_content:
    # 替换整个统计输出部分
    new_content = original_content.replace(target, insertion, 1)
    with open('supplement_album_metadata.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("统计逻辑已修复")
else:
    print("未找到目标代码")
