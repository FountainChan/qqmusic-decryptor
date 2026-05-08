# API 调用异常修复方案

**创建时间**：2026-01-30  
**版本**：v1.0  
**状态**：📋 待确认  
**类型**：修复方案（中文）

---

## 🎯 问题描述

### 当前行为（错误）

```
找到 575 个 FLAC 文件
专辑信息: ['中央芭蕾舞团管弦乐队'] - ['']
WARNING - 未找到 albummid
...
总文件数: 575
成功: 0
失败: 0
跳过: 575  ← 错误：所有文件都被跳过了！
```

### 预期行为（正确）

```
找到 575 个 FLAC 文件
专辑信息: ['中央芭蕾舞团管弦乐队'] - ['']
WARNING - 未找到 albummid
WARNING - 查询专辑信息异常: ...
WARNING - 跳过专辑：未找到发行年份
...
总文件数: 575
成功: 0
失败: 0
跳过: 0  ← 正确：专辑被跳过，不是文件被跳过
```

---

## 🔍 根本原因分析

### 问题 1：缺少异常处理

**位置**：`supplement_album_metadata.py` 第 467-488 行

**当前代码**：
```python
    # 查询 API 获取专辑信息
    if not api_cache:
        album_info = search_album_by_name(f"{artist} {album}")
    else:
        # 检查缓存
        cache_key = f"{artist} - {album}"
        if cache_key in api_cache:
            album_info = api_cache[cache_key]
            logger.info(f"专辑信息已缓存")
        else:
            album_info = search_album_by_name(f"{artist} {album}")
```

**问题**：
- ❌ 没有异常处理
- ❌ 如果 API 调用失败，`album_info` 不会被设置为 `None`
- ❌ 不会触发后续的跳过逻辑

### 问题 2：缺少返回语句

**位置**：`supplement_album_metadata.py` 第 485-503 行

**当前代码**：
```python
    # 获取发行年份
    pub_year = None
    cover_data = None
    
    if album_info and "aDate" in album_info:
        pub_year = album_info["aDate"][:4]  # 只取年份部分
        logger.info(f"找到 aDate: {album_info['aDate']}")
        
        # 获取封面
        albummid = album_info.get("albummid")
        if albummid:
            cover_url = f"https://y.gtimg.cn/music/photo_new/T002R500x500M00000{albummid}.jpg"
            logger.info(f"下载封面: {cover_url}")
            try:
                response = requests.get(cover_url, timeout=API_TIMEOUT)
                response.raise_for_status()
                cover_data = response.content
                logger.info(f"封面数据大小: {len(cover_data)} bytes")
            except Exception as e:
                logger.error(f"下载封面失败: {e}")
        else:
            logger.warning("没有 albummid，无法获取封面")
    else:
        logger.warning("未找到 aDate")
    
    # 处理所有音频文件（FLAC 和 OGG）
    for i, audio_file in enumerate(audio_files):
        ...
```

**问题**：
- ❌ 没有 `return stats` 语句
- ❌ 当找不到 `aDate` 时，处理会继续
- ❌ 所有文件都会被处理，但没有年份和封面
- ❌ 不会跳过专辑，导致所有文件都被处理

---

## 🎯 用户需求确认

### 明确的需求

| 需求 | 说明 | 优先级 |
|------|------|--------|
| 1 | **当找不到 albummid 时，跳过专辑** | 不处理任何文件 | 高 |
| 2 | **当找不到 aDate 时，跳过专辑** | 不处理任何文件 | 高 |
| 3 | **添加异常处理** | 捕获 API 调用异常 | 高 |
| 4 | **添加详细日志** | 显示跳过原因 | 高 |

---

## 🎯 修复方案

### 方案概览

**核心修复**：添加异常处理和跳过逻辑

**修复内容**：
1. ✅ 添加 `try-except` 块处理 API 调用
2. ✅ 当找不到 `aDate` 时，添加跳过逻辑和返回语句
3. ✅ 当找不到 `albummid` 时，只记录警告（不跳过）
4. ✅ 添加详细的日志，显示跳过原因

**不涉及的部分**：
- ❌ 不修改 `supplement_album_metadata.py`（暂时不做修改）
- ❌ 不修改 `qqmusic_api_client.py`（暂时不做修改）
- ❌ 不修改其他文件（暂时不做修改）

---

## 📝 详细修复步骤

### 步骤 1：添加异常处理

**文件**：`supplement_album_metadata.py`  
**位置**：第 467-488 行

**修改前**：
```python
    # 查询 API 获取专辑信息
    if not api_cache:
        album_info = search_album_by_name(f"{artist} {album}")
    else:
        # 检查缓存
        cache_key = f"{artist} - {album}"
        if cache_key in api_cache:
            album_info = api_cache[cache_key]
            logger.info(f"专辑信息已缓存")
        else:
            album_info = search_album_by_name(f"{artist} {album}")
    
    # 获取发行年份
    pub_year = None
    cover_data = None
```

**修改后**：
```python
    # 查询 API 获取专辑信息
    try:
        if not api_cache:
            album_info = search_album_by_name(f"{artist} {album}")
        else:
            # 检查缓存
            cache_key = f"{artist} - {album}"
            if cache_key in api_cache:
                album_info = api_cache[cache_key]
                logger.info(f"专辑信息已缓存")
            else:
                album_info = search_album_by_name(f"{artist} {album}")
    except Exception as e:
        logger.error(f"查询专辑信息异常: {e}")
        album_info = None  # 设置为 None，触发后续跳过逻辑
```

**关键改进**：
- ✅ 添加 `try-except` 块
- ✅ 捕获所有 API 调用异常
- ✅ 设置 `album_info = None`，触发后续跳过逻辑
- ✅ 添加详细的错误日志

---

### 步骤 2：添加跳过逻辑

**文件**：`supplement_album_metadata.py`  
**位置**：第 490-503 行

**修改前**：
```python
    # 获取发行年份
    pub_year = None
    cover_data = None
    
    if album_info and "aDate" in album_info:
        pub_year = album_info["aDate"][:4]  # 只取年份部分
        logger.info(f"找到 aDate: {album_info['aDate']}")
        
        # 获取封面
        albummid = album_info.get("albummid")
        if albummid:
            cover_url = f"https://y.gtimg.cn/music/photo_new/T002R500x500M00000{albummid}.jpg"
            logger.info(f"下载封面: {cover_url}")
            try:
                response = requests.get(cover_url, timeout=API_TIMEOUT)
                response.raise_for_status()
                cover_data = response.content
                logger.info(f"封面数据大小: {len(cover_data)} bytes")
            except Exception as e:
                logger.error(f"下载封面失败: {e}")
        else:
            logger.warning("没有 albummid，无法获取封面")
    else:
        logger.warning("未找到 aDate")
    
    # 处理所有音频文件（FLAC 和 OGG）
    for i, audio_file in enumerate(audio_files):
        ...
```

**修改后**：
```python
    # 获取发行年份
    pub_year = None
    cover_data = None
    
    if album_info and "aDate" in album_info:
        pub_year = album_info["aDate"][:4]  # 只取年份部分
        logger.info(f"找到 aDate: {album_info['aDate']}")
        
        # 获取封面
        albummid = album_info.get("albummid")
        if albummid:
            cover_url = f"https://y.gtimg.cn/music/photo_new/T002R500x500M00000{albummid}.jpg"
            logger.info(f"下载封面: {cover_url}")
            try:
                response = requests.get(cover_url, timeout=API_TIMEOUT)
                response.raise_for_status()
                cover_data = response.content
                logger.info(f"封面数据大小: {len(cover_data)} bytes")
            except Exception as e:
                logger.error(f"下载封面失败: {e}")
        else:
            logger.warning("没有 albummid，无法获取封面")
    else:
        logger.warning("未找到 aDate")
        # 跳过处理（找不到年份和封面）
        logger.warning("跳过专辑：未找到发行年份")
        return stats  # 关键：返回统计信息，跳过专辑
    
    # 处理所有音频文件（FLAC 和 OGG）
    for i, audio_file in enumerate(audio_files):
        ...
```

**关键改进**：
- ✅ 当找不到 `aDate` 时，添加跳过日志
- ✅ 当找不到 `aDate` 时，返回统计信息
- ✅ 当找不到 `aDate` 时，跳过后续处理
- ✅ 添加详细的跳过原因日志

---

## 📊 代码修改汇总

### 修改的文件

| 文件 | 修改类型 | 修改内容 |
|------|----------|----------|
| `supplement_album_metadata.py` | 修改 | API 调用异常处理 + 跳过逻辑 |

### 新增的代码

| 位置 | 代码行数 | 说明 |
|------|----------|------|
| API 调用异常处理（第 467 行） | 约 15 行 | 添加 try-except 块 |
| 跳过逻辑（第 485 行后） | 约 5 行 | 添加返回语句和日志 |

### 总修改量

- **总代码行数**：约 20 行
- **新增功能**：API 调用异常处理 + 跳过逻辑
- **修改风险**：低（向后兼容）

---

## 🎯 预期效果

### 修复前（当前状态）

| 场景 | 专辑信息 | API 调用 | 年份 | 封面 | 处理状态 |
|------|----------|----------|------|------|----------|
| 找不到 albummid | 有 | 失败 | - | - | ❌ 继续处理（所有文件被跳过） |

### 修复后（预期状态）

| 场景 | 专辑信息 | API 调用 | 年份 | 封面 | 处理状态 |
|------|----------|----------|------|------|----------|
| 找不到 albummid | 有 | 失败 | - | - | ✅ 跳过专辑（返回统计） |

### 预期日志输出

```
找到 575 个 FLAC 文件
专辑信息: ['中央芭蕾舞团管弦乐队'] - ['']
WARNING - 未找到 albummid  ← 关键验证点
WARNING - 跳过专辑：未找到发行年份  ← 关键验证点
...
==================================================
处理完成
==================================================

总文件数: 575
成功: 0  ← 正确：没有处理文件
失败: 0  ← 正确：没有失败
跳过: 0  ← 正确：专辑被跳过，不是文件被跳过
```

---

## 🎯 功能特性

### API 调用异常处理

| 功能 | 状态 | 说明 |
|------|------|------|
| 异常捕获 | ✅ 支持 | 捕获所有 API 调用异常 |
| 错误日志 | ✅ 支持 | 记录详细的错误信息 |
| 降级处理 | ✅ 支持 | 设置 `album_info = None`，触发跳过逻辑 |

### 跳过逻辑

| 功能 | 状态 | 说明 |
|------|------|------|
| 跳过日志 | ✅ 支持 | 显示跳过原因 |
| 返回统计 | ✅ 支持 | 返回统计信息，不处理文件 |
| 详细日志 | ✅ 支持 | 记录所有跳过细节 |

---

## 🚀 实施计划

### 计划 1：代码修改

- [ ] **步骤 1**：添加 API 调用异常处理（添加 try-except 块）
- [ ] **步骤 2**：添加跳过逻辑（添加返回语句和日志）

### 计划 2：功能测试

- [ ] **测试 1**：测试找不到 albummid 时的跳过逻辑
- [ ] **测试 2**：验证跳过日志是否正确显示
- [ ] **测试 3**：验证统计信息是否正确

### 计划 3：文档更新

- [ ] **文档 1**：创建中文测试方案文档
- [ ] **文档 2**：创建最终报告文档

---

## 📋 实施注意事项

### 注意事项 1：异常处理

**说明**：
- ✅ 添加 `try-except` 块处理 API 调用
- ✅ 捕获所有异常（包括网络异常、超时异常等）
- ✅ 设置 `album_info = None`，触发后续跳过逻辑

**好处**：
- ✅ 避免程序崩溃
- ✅ 提供详细的错误信息
- ✅ 触发正确的跳过逻辑

### 注意事项 2：跳过逻辑

**说明**：
- ✅ 当找不到 `aDate` 时，添加跳过日志
- ✅ 当找不到 `aDate` 时，返回统计信息
- ✅ 当找不到 `aDate` 时，跳过后续处理

**好处**：
- ✅ 避免无效的处理
- ✅ 提高处理效率
- ✅ 减少无效的日志

---

## 📊 修改前后对比

### 修改前（当前状态）

| 指标 | 修复前 |
|------|--------|
| 异常处理 | ❌ 没有 |
| 跳过逻辑 | ❌ 没有 |
| 跳过日志 | ❌ 没有 |
| 返回语句 | ❌ 没有 |
| 所有文件被跳过 | ❌ 错误 |

### 修复后（预期状态）

| 指标 | 修复后 |
|------|--------|
| 异常处理 | ✅ 有 |
| 跳过逻辑 | ✅ 有 |
| 跳过日志 | ✅ 有 |
| 返回语句 | ✅ 有 |
| 专辑被跳过 | ✅ 正确 |

---

## 📝 相关文档

- **OGG 音轨号写入实施方案**：`docs/OGG音轨号写入实施方案.md`（已实现）
- **OGG 音轨号写入测试方案**：`docs/OGG音轨号写入测试方案.md`（已实现）
- **OGG 元数据支持文档**：`docs/OGG_METADATA_IMPLEMENTATION_RESULT.md`（已实现）
- **封面保存位置修复文档**：`docs/封面保存位置修复实施方案.md`（已实现）

---

## 🎯 下一步行动

### 等待用户确认

**待确认**：
1. ❓ **是否按照上述方案进行代码修改？**
2. ❓ **是否需要创建详细的测试方案文档？**
3. ❓ **是否需要创建最终的报告文档？**

### 如果确认实施

**我会执行**：
1. ✅ 添加 API 调用异常处理（添加 try-except 块）
2. ✅ 添加跳过逻辑（添加返回语句和日志）
3. ✅ 创建详细的测试方案文档
4. ✅ 创建最终报告文档
5. ✅ 运行测试验证功能

### 如果需要调整

**请告诉我**：
1. ❓ 需要调整实施方案吗？
2. ❓ 需要调整测试方案吗？
3. ❓ 需要添加其他功能吗？

---

## 📋 总结

### ✅ 修复方案完成

1. ✅ **问题分析完成**：已确认 API 调用异常和跳过逻辑问题
2. ✅ **用户需求明确**：已确认 4 个具体需求
3. ✅ **详细实施步骤**：已制定 2 个修改步骤
4. ✅ **代码修改计划**：已明确所有需要修改的代码
5. ✅ **预期效果定义**：已明确所有预期结果

### 🎯 推荐方案

**方案**：添加异常处理和跳过逻辑

**理由**：
- ✅ 避免程序崩溃
- ✅ 提供详细的错误信息
- ✅ 触发正确的跳过逻辑
- ✅ 避免无效的处理
- ✅ 提高处理效率

---

## 📚 相关文档

- **实施计划**：本文档（`docs/API调用异常修复方案.md`）
- **跳过逻辑修复方案**：`docs/跳过逻辑修复方案.md`（待创建）
- **测试方案**：`docs/API调用异常测试方案.md`（待创建）
- **OGG 支持文档**：`docs/OGG_METADATA_IMPLEMENTATION_RESULT.md`（已实现）

---

**文档创建时间**：2026-01-30  
**最后更新**：2026-01-30  
**维护者**：AI 助手
