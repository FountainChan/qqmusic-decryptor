# OGG 元数据支持实施计划

**创建时间**：2026-01-29  
**版本**：v2.0  
**状态**：⏳ 待确认  
**类型**：实施计划

---

## 📋 问题分析

### 当前状态
- ✅ **扫描修复**：脚本能找到 `.ogg` 文件（之前只能找 `.flac`）
- ❌ **标签读取失败**：使用 `FLAC()` 类读取 `.ogg` 文件时报错
- ❌ **元数据写入失败**：尝试用 `FLAC()` 类写入 `.ogg` 文件失败
- ❌ **所有文件被跳过**：因为标签提取失败，导致无法继续后续流程

### 根本原因

**问题 1：标签提取函数不支持 OGG**
- **函数**：`extract_flac_tags(flac_file_path)`
- **限制**：只使用 `mutagen.flac.FLAC` 类
- **错误**：`'...' is not a valid FLAC file`（当处理 .ogg 时）

**问题 2：元数据嵌入函数不支持 OGG**
- **函数**：`embed_metadata_to_flac(flac_file_path, pub_year, cover_data)`
- **限制**：只使用 `mutagen.flac.FLAC` 类
- **错误**：无法处理 `.ogg` 文件

**问题 3：函数调用名称不匹配**
- **位置**：`supplement_album_metadata.py` 第 420 行
- **错误**：调用了一个不存在的函数 `process_single_audio_metadata()`

---

## 🎯 设计决策

### 决策 1：OGG 元数据写入策略

**选项 A**：完整支持（文本 + 封面）
- **优点**：功能完整
- **缺点**：OGG 封面嵌入非常复杂，容易出错，兼容性差

**选项 B**：仅文本元数据 + 封面文件（推荐）
- **优点**：实现简单、稳定、兼容性好
- **缺点**：封面只作为独立文件（`cover.jpg`），不内嵌

**最终决策**：**选项 B** - 仅文本元数据 + 封面文件

**理由**：
- OGG 封面嵌入是业界的难题（Vorbis comments 格式复杂）
- 很多播放器不支持或显示 OGG 内嵌封面异常
- `cover.jpg` 独立文件已经是标准的做法，兼容性最好

---

## 🚀 实施计划

### 步骤 1：添加 OGG 库导入

**文件**：`supplement_album_metadata.py`  
**位置**：文件顶部（约第 10-20 行）

**操作**：
```python
# 现有导入
from mutagen.flac import FLAC

# 添加 OGG 支持
from mutagen.oggvorbis import OggVorbis
```

**说明**：
- 添加 `OggVorbis` 类用于处理 OGG 文件
- 保留现有的 `FLAC` 类用于处理 FLAC 文件

---

### 步骤 2：创建统一的标签提取函数

**文件**：`supplement_album_metadata.py`  
**函数名**：`extract_audio_tags(audio_file_path)`

**操作**：创建新函数，替换 `extract_flac_tags()` 功能

**代码框架**：
```python
def extract_audio_tags(audio_file_path):
    """
    从音频文件提取标签（支持 FLAC 和 OGG）
    
    Args:
        audio_file_path: 音频文件路径（.flac 或 .ogg）
    
    Returns:
        dict: {'artist': str, 'album': str, 'title': str}
    """
    try:
        filename = audio_file_path.lower()
        
        # 根据文件类型选择提取方式
        if filename.endswith('.flac'):
            # FLAC 文件：使用 FLAC 类
            audio = FLAC(audio_file_path)
            artist = audio.get("ARTIST", [None])[0]
            album = audio.get("ALBUM", [None])[0]
            title = audio.get("TITLE", [None])[0]
            
        elif filename.endswith('.ogg'):
            # OGG 文件：使用 OggVorbis 类
            audio = OggVorbis(audio_file_path)
            # OGG 标签访问方式与 FLAC 不同（使用 tags 字典）
            artist = audio.get("ARTIST")
            if artist:
                artist = str(artist)
            album = audio.get("ALBUM")
            if album:
                album = str(album)
            title = audio.get("TITLE")
            if title:
                title = str(title)
            
        else:
            # 不支持的格式
            logger.error(f"不支持的文件格式: {audio_file_path}")
            return {"artist": None, "album": None, "title": None}
        
        return {
            "artist": artist or "",
            "album": album or "",
            "title": title or ""
        }
        
    except Exception as e:
        logger.error(f"读取标签失败 {audio_file_path}: {e}")
        return {"artist": None, "album": None, "title": None}
```

**技术细节**：
- **FLAC 处理**：与之前相同，使用 `audio.get("TAG", [None])[0]`
- **OGG 处理**：使用 `audio.get("TAG")`，并转换为字符串
- **错误处理**：捕获所有异常，返回空字典

---

### 步骤 3：创建统一的元数据嵌入函数

**文件**：`supplement_album_metadata.py`  
**函数名**：`embed_metadata_to_audio(audio_file_path, pub_year, cover_data)`

**操作**：创建新函数，支持 FLAC 和 OGG 的文本元数据写入

**代码框架**：
```python
def embed_metadata_to_audio(audio_file_path, pub_year, cover_data):
    """
    将元数据嵌入音频文件（支持 FLAC 和 OGG）
    
    Args:
        audio_file_path: 音频文件路径（.flac 或 .ogg）
        pub_year: 发行年份（字符串，如 "2009"）
        cover_data: 封面数据
    
    Returns:
        bool: 成功返回 True
    """
    try:
        filename = audio_file_path.lower()
        
        if filename.endswith('.flac'):
            # FLAC 文件处理
            audio = FLAC(audio_file_path)
            
            # 清除现有封面
            audio.clear_pictures()
            
            # 添加年份（DATE 标签）
            if pub_year:
                audio["DATE"] = pub_year
                logger.info(f"添加年份 (FLAC): {pub_year}")
            
            # 添加封面（PICTURE 标签）
            if cover_data:
                image = Picture()
                image.type = 3
                image.mime = "image/jpeg"
                image.data = cover_data
                
                audio.add_picture(image)
                logger.info(f"嵌入封面 (FLAC)")
            
            # 保存
            audio.save()
            logger.info(f"保存元数据 (FLAC): {os.path.basename(audio_file_path)}")
            return True
            
        elif filename.endswith('.ogg'):
            # OGG 文件处理（仅文本元数据）
            audio = OggVorbis(audio_file_path)
            
            # 添加年份（DATE 标签）
            if pub_year:
                # OGG Vorbis 标准使用 DATE 字符串
                audio["DATE"] = pub_year
                logger.info(f"添加年份 (OGG): {pub_year}")
            
            # 封面处理：跳过内嵌，只保存为独立文件
            # OGG Vorbis 的封面嵌入需要手动构建 METADATA_BLOCK_PICTURE
            # 为了稳定性和兼容性，我们跳过内嵌
            # cover.jpg 会在主函数中单独保存
            if cover_data:
                logger.info(f"OGG 封面只保存为独立文件，不内嵌")
            else:
                logger.info(f"没有封面数据")
            
            # 保存
            audio.save()
            logger.info(f"保存元数据 (OGG): {os.path.basename(audio_file_path)}")
            return True
            
        else:
            # 不支持的格式
            logger.error(f"不支持的文件格式: {audio_file_path}")
            return False
            
    except Exception as e:
        logger.error(f"嵌入元数据失败 {audio_file_path}: {e}")
        return False
```

**技术决策**：
- **FLAC 文件**：
  - ✅ 完整支持：DATE + PICTURE
  - ✅ 使用标准的 FLAC 元数据结构

- **OGG 文件**：
  - ✅ 只支持：DATE（文本）
  - ❌ 跳过：PICTURE（封面内嵌）
  - **理由**：
    1. OGG Vorbis 的封面嵌入非常复杂（需要手动构建二进制 METADATA_BLOCK_PICTURE）
    2. 容易出错，很难调试
    3. 很多播放器不支持或显示 OGG 内嵌封面异常
    4. `cover.jpg` 独立文件已经是标准的做法，兼容性最好

---

### 步骤 4：更新主函数调用

**文件**：`supplement_album_metadata.py`

**操作 1**：更新第 348 行的函数调用

**位置**：`process_root_directory()` 函数中的标签提取

**修改前**：
```python
first_audio = audio_files[0]
tags = extract_flac_tags(first_audio)
```

**修改后**：
```python
first_audio = audio_files[0]
tags = extract_audio_tags(first_audio)
```

**操作 2**：更新第 424 行的函数调用

**位置**：`process_root_directory()` 函数中的元数据嵌入

**修改前**：
```python
# 嵌入元数据
filename = os.path.basename(audio_file)
success = embed_metadata_to_flac(audio_file, pub_year, cover_data)
```

**修改后**：
```python
# 嵌入元数据
filename = os.path.basename(audio_file)
success = embed_metadata_to_audio(audio_file, pub_year, cover_data)
```

---

## 📊 预期效果

### 修复前的行为

```
输入：01 歌曲.ogg
结果：[ERROR] 读取标签失败 '...' is not a valid FLAC file
效果：文件被拒绝，不会添加任何元数据 ❌
```

### 修复后的行为

```
输入：01 歌曲.ogg
步骤 1：扫描 ✅ 找到文件
步骤 2：提取标签 ✅ 使用 OggVorbis 类读取
步骤 3：API 调用 ✅ 获取专辑信息和年份
步骤 4：下载封面 ✅ 下载封面数据
步骤 5：写入年份 ✅ 使用 audio["DATE"] 写入
步骤 6：跳过封面内嵌 ✅ 不内嵌，只保存为 cover.jpg
步骤 7：保存元数据 ✅ audio.save()
结果：✅ 成功处理
效果：文件被接受，元数据正确写入 ✅
```

---

## 🎯 实施总结

### 需要修改的文件

**文件**：`supplement_album_metadata.py`  
**修改行数**：约 150 行（新函数 + 更新调用）

### 需要添加的代码

1. **新函数**：`extract_audio_tags(audio_file_path)` （约 60 行）
2. **新函数**：`embed_metadata_to_audio(audio_file_path, pub_year, cover_data)` （约 80 行）
3. **导入**：`from mutagen.oggvorbis import OggVorbis`（1 行）

### 需要更新的代码

1. **函数调用 1**：`extract_flac_tags()` → `extract_audio_tags()` （第 348 行）
2. **函数调用 2**：`embed_metadata_to_flac()` → `embed_metadata_to_audio()` （第 424 行）

---

## 🧪 测试计划

### 测试 1：导入验证
**命令**：
```bash
cd /d/WorkDev/qqmusic_decryptor
python -c "from mutagen.oggvorbis import OggVorbis; print('✅ OGG 库导入成功')"
```

**预期结果**：
- ✅ 如果 `mutagen` 已正确安装
- ❌ 如果提示 `ModuleNotFoundError`

### 测试 2：单个 OGG 文件测试
**命令**：
```bash
cd /d/WorkDev/qqmusic_decryptor
./run_supplement.sh "/g/QQMusic/Decrypted/VipSongsDownload/侧田/From Justin (Collection Of His First 3 Years)"
```

**预期结果**：
```
[INFO] 找到 X 个音频文件（.flac/.ogg）
[INFO] 专辑信息: 侧田 - From Justin ...
[INFO] 添加年份 (OGG): 2009
[INFO] OGG 封面只保存为独立文件，不内嵌
[INFO] 保存元数据 (OGG): 01 歌曲.ogg
[OK] 01 歌曲.ogg
```

**关键检查点**：
- ✅ 能找到 `.ogg` 文件
- ✅ 能正确读取 OGG 标签
- ✅ 能正确写入 DATE 标签
- ✅ 封面文件正确保存

### 测试 3：批量测试
**命令**：
```bash
cd /d/WorkDev/qqmusic_decryptor
./run_supplement.sh "G:\QQMusic\Decrypted\VipSongsDownload"
```

**预期结果**：
- ✅ 所有 `.flac` 文件正常处理（年份 + 内嵌封面）
- ✅ 所有 `.ogg` 文件正常处理（年份 + 封面文件）
- ✅ 智能缓存正常工作
- ✅ 统计信息正确显示

---

## 📝 注意事项

### 1. OGG 封面说明
- **行为**：OGG 文件不会内嵌封面
- **替代**：封面只保存为独立的 `cover.jpg` 文件
- **理由**：
  - OGG Vorbis 封面嵌入复杂且不稳定
  - 很多播放器不支持或显示异常
  - 独立 `cover.jpg` 是行业标准做法

### 2. 元数据限制
- **OGG 文件**：只支持 DATE（年份）标签
- **FLAC 文件**：完全支持（DATE + PICTURE）
- **说明**：如果需要 OGG 的更多元数据支持（如 TRACKNUMBER），需要后续开发

### 3. 兼容性
- **OGG 文件**：修改后的 OGG 文件与所有播放器兼容
- **封面文件**：`cover.jpg` 与所有播放器和媒体管理器兼容

### 4. 依赖检查
- **mutagen**：应该已经安装（用于 FLAC 处理）
- **OggVorbis**：包含在标准 `mutagen` 包中
- **安装命令**：`pip install mutagen`（如果没有安装）

---

## 🎉 实施完成后的效果

### 对于 FLAC 文件
- ✅ 完整支持：DATE + PICTURE
- ✅ 年份正确内嵌
- ✅ 封面正确内嵌
- ✅ 封面文件正确保存

### 对于 OGG 文件
- ✅ 文本支持：DATE（年份）
- ✅ 年份正确写入
- ✅ 封面文件正确保存（`cover.jpg`）
- ⚠️ 限制：不支持封面内嵌（设计决策）

### 整体效果
- ✅ 所有 `.flac` 文件正常处理
- ✅ 所有 `.ogg` 文件正常处理
- ✅ 不会再跳过 OGG 文件
- ✅ 元数据正确写入
- ✅ 封面文件正确保存

---

## 🚀 实施顺序

1. ✅ **添加 OGG 库导入**（第 10-20 行）
2. ✅ **创建 `extract_audio_tags()` 函数**（约 60 行）
3. ✅ **创建 `embed_metadata_to_audio()` 函数**（约 80 行）
4. ✅ **更新主函数调用**（第 348 行 + 第 424 行）
5. ✅ **测试验证**
6. ✅ **文档更新**

---

## 📊 实施统计

### 代码变更

- **新增代码**：约 150 行
  - 新函数：2 个（~140 行）
  - 导入：1 行
  - 函数调用更新：2 处

- **修改代码**：0 行（只更新函数调用，不修改逻辑）

- **删除代码**：0 行（保留旧函数以供参考）

### 文件变更

- **修改文件**：1 个
  - `supplement_album_metadata.py`

---

## 📚 相关文档

- **AGENTS.md**：AI 助手规则和最佳实践
- **test/README.md**：测试脚本指南
- **doc/RUN_SCRIPT_GUIDE.md**：一键运行脚本使用指南
- **doc/ALBUM_METADATA_FEATURE.md**：专辑元数据功能说明

---

## 🎯 实施确认

**请确认以上实施计划是否符合你的预期？**

**关键决策点**：
1. ✅ 是否接受 OGG 只支持文本元数据（DATE）？
2. ✅ 是否接受 OGG 封面只保存为独立文件（不内嵌）？
3. ✅ 是否按照上述实施顺序进行修改？
4. ✅ 是否在修改后进行完整的测试？

**如果有任何疑问或需要调整的地方，请告诉我！**

---

**确认后，我将严格按照本计划文档进行代码修改和实施。**

---

**文档创建时间**：2026-01-29  
**最后更新**：2026-01-29  
**维护者**：AI 助手
