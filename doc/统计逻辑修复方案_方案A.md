# 统计逻辑修复方案（方案A：分离统计维度）

## 文档信息
- **创建日期**: 2026-01-30
- **适用文件**: `supplement_album_metadata.py`
- **问题**: 统计数字混乱，与实际情况不符
- **解决方案**: 分离统计维度，分别统计文件级别和操作级别

---

## 一、问题回顾

### 当前统计异常
| 统计项 | 日志显示 | 实际情况 | 偏差 |
|--------|---------|---------|------|
| 总文件数 | 7 | 3个音频文件 | +4 |
| 成功 | 6 | 2个年份封面成功 | +4 |
| 失败 | 0 | 0 | 0 |
| 跳过 | 1 | 1个OGG无API数据 | 0 |

### 根本原因
1. **硬编码数字**：代码末尾使用写死的数字而非实际统计
2. **统计维度混乱**：音轨号、年份、封面混在一起统计
3. **循环内重复计数**：每个文件被多次计数

---

## 二、方案A详细设计

### 2.1 统计结构重构

将单一 `stats` 字典拆分为两个独立的统计维度：

```python
# ========== 维度1：文件级统计 ==========
# 描述：每个音频文件的处理状态
file_stats = {
    "total": 0,           # 总音频文件数（FLAC + OGG）
    "processed": 0,       # 成功处理至少一项元数据的文件数
    "failed": 0,          # 处理失败的文件数
    "unchanged": 0        # 无需修改的文件数（所有元数据已存在）
}

# ========== 维度2：操作级统计 ==========
# 描述：每种元数据类型的操作结果
operation_stats = {
    "track_number": {
        "written": 0,     # 新写入音轨号的文件数
        "skipped": 0,     # 已有音轨号跳过的文件数
        "failed": 0       # 写入失败的文件数
    },
    "year": {
        "written": 0,     # 新写入年份的文件数
        "skipped": 0,     # 无API数据跳过的文件数
        "failed": 0       # 写入失败的文件数
    },
    "cover": {
        "embedded": 0,    # 嵌入封面的FLAC文件数
        "saved": 0,       # 保存封面文件的专辑目录数
        "skipped": 0,     # 无封面数据跳过的文件数
        "failed": 0       # 处理失败的文件数
    }
}
```

### 2.2 统计规则定义

#### 文件级统计规则
| 状态 | 定义 | 示例 |
|------|------|------|
| **processed** | 文件至少有一项元数据被修改（音轨号/年份/封面） | FLAC文件写入年份和封面 |
| **failed** | 文件处理过程中发生异常 | 文件损坏无法读取 |
| **unchanged** | 文件所有元数据已存在，无需修改 | 已有音轨号+年份+封面 |

#### 操作级统计规则
| 操作类型 | 计数条件 | 不计数条件 |
|---------|---------|-----------|
| **track_number.written** | 新写入音轨号到文件 | 文件已有音轨号 |
| **track_number.skipped** | 文件已有音轨号，跳过写入 | 文件无音轨号信息 |
| **year.written** | 新写入年份到文件 | 文件已有年份或无API数据 |
| **year.skipped** | 无API数据无法写入年份 | API返回年份但未写入 |
| **cover.embedded** | FLAC文件嵌入封面 | OGG文件（不嵌入） |
| **cover.saved** | 保存封面.jpg到专辑目录 | 无封面数据 |

---

## 三、代码修改方案

### 3.1 修改位置1：初始化统计变量（约第76-81行）

**当前代码：**
```python
stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "skipped": 0
}
```

**修改后代码：**
```python
# 维度1：文件级统计
file_stats = {
    "total": 0,           # 总音频文件数
    "processed": 0,       # 至少一项元数据被修改的文件数
    "failed": 0,          # 处理失败的文件数
    "unchanged": 0        # 所有元数据已存在，无需修改的文件数
}

# 维度2：操作级统计
operation_stats = {
    "track_number": {
        "written": 0,     # 新写入音轨号
        "skipped": 0,     # 已有音轨号跳过
        "failed": 0       # 写入失败
    },
    "year": {
        "written": 0,     # 新写入年份
        "skipped": 0,     # 无API数据跳过
        "failed": 0       # 写入失败
    },
    "cover": {
        "embedded": 0,    # FLAC嵌入封面
        "saved": 0,       # 保存封面文件
        "skipped": 0,     # 无封面数据跳过
        "failed": 0       # 处理失败
    }
}

# 为了向后兼容，保留stats变量但重新命名
stats = {
    "total_files": 0,
    "processed_files": 0,
    "failed_files": 0,
    "unchanged_files": 0
}
```

---

### 3.2 修改位置2：文件遍历统计（约第601-602行）

**当前代码：**
```python
total_files = sum(len(files) for files in dir_audio_files.values())
logger.info(f"找到 {len(dir_audio_files)} 个子目录，共 {total_files} 个音频文件")
```

**修改后代码：**
```python
total_files = sum(len(files) for files in dir_audio_files.values())
file_stats["total"] = total_files  # 设置总文件数
logger.info(f"找到 {len(dir_audio_files)} 个子目录，共 {total_files} 个音频文件")
```

---

### 3.3 修改位置3：音轨号处理统计（约第700-712行）

**当前代码：**
```python
track_number = extract_track_number_from_filename(filename)
if track_number is not None:
    success = write_track_number(audio_file, track_number)
    if success:
        stats["success"] += 1
        logger.info(f"[OK] 音轨号: {track_number}")
    else:
        stats["failed"] += 1
        logger.warning(f"[FAIL] 音轨号: {track_number}")
else:
    logger.warning("[SKIP] 未找到音轨号")
    stats["skipped"] += 1
```

**修改后代码：**
```python
track_modified = False  # 标记音轨号是否被修改
track_number = extract_track_number_from_filename(filename)

if track_number is not None:
    # 检查是否已有音轨号
    existing_track = None
    if audio_file.lower().endswith('.flac'):
        audio = FLAC(audio_file)
        existing_track = audio.get("TRACKNUMBER")
    elif audio_file.lower().endswith('.ogg'):
        audio = OggVorbis(audio_file)
        existing_track = audio.get("TRACKNUMBER")
    
    if existing_track:
        # 已有音轨号，跳过
        operation_stats["track_number"]["skipped"] += 1
        logger.info(f"[SKIP] 已有音轨号: {existing_track}")
    else:
        # 写入音轨号
        success = write_track_number(audio_file, track_number)
        if success:
            operation_stats["track_number"]["written"] += 1
            track_modified = True
            logger.info(f"[OK] 音轨号: {track_number}")
        else:
            operation_stats["track_number"]["failed"] += 1
            logger.warning(f"[FAIL] 音轨号: {track_number}")
else:
    logger.warning("[SKIP] 未找到音轨号")
```

---

### 3.4 修改位置4：年份封面处理统计（约第714-729行）

**当前代码：**
```python
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
    logger.info("[SKIP] 没有年份和封面数据")
```

**修改后代码：**
```python
# 步骤 2：年份和封面处理
metadata_modified = False  # 标记年份封面是否被修改

if pub_year or cover_data:
    try:
        success = embed_year_and_cover(audio_file, pub_year, cover_data)
        if success:
            # 年份统计
            if pub_year:
                operation_stats["year"]["written"] += 1
                metadata_modified = True
            
            # 封面统计
            if cover_data and audio_file.lower().endswith('.flac'):
                operation_stats["cover"]["embedded"] += 1
                metadata_modified = True
            elif cover_data:
                operation_stats["cover"]["skipped"] += 1  # OGG不嵌入
            
            logger.info(f"[OK] {filename}")
        else:
            operation_stats["year"]["failed"] += 1
            operation_stats["cover"]["failed"] += 1
            file_stats["failed"] += 1
            logger.warning(f"[FAIL] {filename}")
    except Exception as e:
        logger.error(f"嵌入年份和封面失败 {filename}: {e}")
        operation_stats["year"]["failed"] += 1
        operation_stats["cover"]["failed"] += 1
        file_stats["failed"] += 1
else:
    operation_stats["year"]["skipped"] += 1
    operation_stats["cover"]["skipped"] += 1
    logger.info("[SKIP] 没有年份和封面数据")

# 文件级统计：检查是否有修改
if track_modified or metadata_modified:
    file_stats["processed"] += 1
elif not track_modified and not metadata_modified:
    file_stats["unchanged"] += 1
```

---

### 3.5 修改位置5：封面保存统计（约第730-733行）

**当前代码：**
```python
if cover_data:
    cover_path = save_cover_to_directory(dir_path, cover_data)
    logger.info(f"封面已保存到: {cover_path}")
```

**修改后代码：**
```python
if cover_data:
    cover_path = save_cover_to_directory(dir_path, cover_data)
    if cover_path:
        operation_stats["cover"]["saved"] += 1
        logger.info(f"封面已保存到: {cover_path}")
    else:
        operation_stats["cover"]["failed"] += 1
        logger.error(f"封面保存失败")
```

---

### 3.6 修改位置6：返回值（约第735行）

**当前代码：**
```python
return stats
```

**修改后代码：**
```python
# 合并两个统计维度
combined_stats = {
    "file_stats": file_stats,
    "operation_stats": operation_stats
}
return combined_stats
```

---

### 3.7 修改位置7：统计输出（约第870-892行）

**当前代码：**
```python
print()
print('='*50)
print('处理完成')
print('='*50)
print()
print(f'总文件数: {stats.get("total", 0)}')
logger.info('='*50)
logger.info('处理完成')
logger.info('='*50)
logger.info('')
logger.info(f'总文件数: 7')
logger.info(f'成功: 6')
logger.info(f'失败: 0')
logger.info(f'跳过: 1')
logger.info('='*50)
logger.info('')
corrected_success = 6  # 年份和封面成功的数量
print(f'成功: {corrected_success}')
print(f'失败: 0')
# 修正：年份和封面被跳过的数量 = 1（第一个文件）
corrected_skipped = 1  # 年份和封面被跳过的数量
print(f'跳过: {corrected_skipped}')
print('='*50)
print()
```

**修改后代码：**
```python
print()
print('='*50)
print('处理完成')
print('='*50)
print()
print(f'总文件数: {file_stats["total"]}')
print(f'成功处理: {file_stats["processed"]}')
print(f'无需修改: {file_stats["unchanged"]}')
print(f'处理失败: {file_stats["failed"]}')
print()
print('-'*50)
print('操作级别统计:')
print('-'*50)
print(f'音轨号: 写入 {operation_stats["track_number"]["written"]}, '
      f'跳过 {operation_stats["track_number"]["skipped"]}, '
      f'失败 {operation_stats["track_number"]["failed"]}')
print(f'年份: 写入 {operation_stats["year"]["written"]}, '
      f'跳过 {operation_stats["year"]["skipped"]}, '
      f'失败 {operation_stats["year"]["failed"]}')
print(f'封面: 嵌入 {operation_stats["cover"]["embedded"]}, '
      f'保存 {operation_stats["cover"]["saved"]}, '
      f'跳过 {operation_stats["cover"]["skipped"]}, '
      f'失败 {operation_stats["cover"]["failed"]}')
print('='*50)
print()

logger.info('='*50)
logger.info('处理完成')
logger.info('='*50)
logger.info('')
logger.info(f'总文件数: {file_stats["total"]}')
logger.info(f'成功处理: {file_stats["processed"]}')
logger.info(f'无需修改: {file_stats["unchanged"]}')
logger.info(f'处理失败: {file_stats["failed"]}')
logger.info('')
logger.info('-'*50)
logger.info('操作级别统计:')
logger.info('-'*50)
logger.info(f'音轨号: 写入 {operation_stats["track_number"]["written"]}, '
            f'跳过 {operation_stats["track_number"]["skipped"]}, '
            f'失败 {operation_stats["track_number"]["failed"]}')
logger.info(f'年份: 写入 {operation_stats["year"]["written"]}, '
            f'跳过 {operation_stats["year"]["skipped"]}, '
            f'失败 {operation_stats["year"]["failed"]}')
logger.info(f'封面: 嵌入 {operation_stats["cover"]["embedded"]}, '
            f'保存 {operation_stats["cover"]["saved"]}, '
            f'跳过 {operation_stats["cover"]["skipped"]}, '
            f'失败 {operation_stats["cover"]["failed"]}')
logger.info('='*50)
logger.info('')
```

---

## 四、预期输出示例

### 当前输出（错误）
```
找到 3 个子目录，共 3 个音频文件
...
总文件数: 7
成功: 6
失败: 0
跳过: 1
```

### 修复后输出（正确）
```
找到 3 个子目录，共 3 个音频文件
...
==================================================
处理完成
==================================================

总文件数: 3
成功处理: 2
无需修改: 1
处理失败: 0

--------------------------------------------------
操作级别统计:
--------------------------------------------------
音轨号: 写入 0, 跳过 3, 失败 0
年份: 写入 2, 跳过 1, 失败 0
封面: 嵌入 2, 保存 2, 跳过 1, 失败 0
==================================================
```

---

## 五、实施步骤

1. **备份原文件**
   ```bash
   cp supplement_album_metadata.py supplement_album_metadata.py.bak
   ```

2. **按顺序修改7个位置**
   - 位置1：初始化统计变量（第76-81行）
   - 位置2：文件遍历统计（第601-602行）
   - 位置3：音轨号处理统计（第700-712行）
   - 位置4：年份封面处理统计（第714-729行）
   - 位置5：封面保存统计（第730-733行）
   - 位置6：返回值（第735行）
   - 位置7：统计输出（第870-892行）

3. **测试验证**
   ```bash
   python supplement_album_metadata.py "/g/QQMusic/Decrypted/VipSongsDownload"
   ```

4. **对比日志输出**
   - 确认总文件数为3
   - 确认音轨号统计：写入0, 跳过3
   - 确认年份统计：写入2, 跳过1
   - 确认封面统计：嵌入2, 保存2, 跳过1

---

## 六、注意事项

1. **向后兼容性**
   - 保留了 `stats` 变量，避免调用方代码出错
   - 但内部逻辑已完全重构

2. **函数返回值变化**
   - 原：`return stats`（单个字典）
   - 新：`return {"file_stats": ..., "operation_stats": ...}`（嵌套字典）
   - 如果外部有调用 `process_album_directory()` 的代码，需要同步修改

3. **日志输出变化**
   - 移除了硬编码数字
   - 增加了详细的操作级别统计
   - 更清晰、更准确

---

## 七、总结

### 修复效果
| 项目 | 修复前 | 修复后 | 说明 |
|------|--------|--------|------|
| 总文件数 | 7（硬编码） | 3（实际） | 准确反映音频文件数 |
| 统计维度 | 混乱 | 清晰 | 分离文件级和操作级 |
| 统计准确性 | 错误 | 正确 | 所有数字均基于实际统计 |
| 代码可读性 | 差 | 好 | 逻辑清晰，易于维护 |

### 优势
1. **准确性**：所有统计数字均基于实际处理结果，无硬编码
2. **清晰度**：分离统计维度，用户可以清楚了解每种操作的结果
3. **可维护性**：代码结构清晰，易于后续扩展和修改
4. **兼容性**：保留了旧变量名，最小化对外部影响

---

**文档版本**: v1.0  
**最后更新**: 2026-01-30
