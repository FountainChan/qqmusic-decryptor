# 日期修复和元数据补充实施计划

## 📋 项目概述

**项目名称**：QQ Music 解密工具 - 日期修复和元数据补充
**创建时间**：2026-01-29
**目标**：修复日期未写入问题，并创建独立补充脚本

---

## 🔍 问题分析

### 根本原因

**API 返回的数据结构**：

```json
{
  "response": {
    "code": 0,
    "data": {
      "aDate": "2015-06-11",  ← 正确的字段名！
      "list": [
        {
          "albummid": "000ILKG63fED7K",
          "albumname": "Never Odd Or Even",
          "albumdesc": "2015年We Touch..."
        }
      ]
    }
  }
}
```

**当前代码问题**：

```python
# 错误的字段名（有下划线）
pub_time = album_info.get("pub_time")  # 返回 None

# 正确的字段名（无下划线）
aDate = album_info.get("aDate")  # 返回 "2015-06-11"
```

### 问题影响

1. **日期未写入**：
   - `pub_year = ""`（空字符串）
   - `pub_date = ""`（空字符串）
   - FLAC 文件没有 DATE 标签

2. **封面成功但日期缺失**：
   - 封面成功嵌入到 FLAC 文件
   - cover.jpg 成功保存到专辑目录
   - 但发行年份缺失

---

## ✅ 解决方案

### 方案 1：修复 API 调用（推荐）

**文件**：`qqmusic_api_client.py`

**修改内容**：

#### 1.1 新增方法：`get_album_info_with_date()`

```python
def get_album_info_with_date(self, albummid: str) -> Optional[Dict]:
    """
    获取专辑详细信息（使用 aDate 字段）
    
    Args:
        albummid: 专辑 ID
    
    Returns:
        包含专辑详细信息的字典，失败返回 None
    """
    try:
        response = self.session.get(
            f"{self.base_url}/getAlbumInfo",
            params={"albummid": albummid},
            timeout=self.timeout
        )
        response.raise_for_status()
        
        data = response.json()
        
        if "response" not in data or "data" not in data["response"]:
            logger.error(f"获取专辑信息失败：{albummid}")
            return None
        
        album_info = data["response"]["data"]["list"][0]
        
        # 直接从 data 层级获取 aDate 字段
        response_data = data["response"]["data"]
        a_date = response_data.get("aDate")
        
        # 处理日期
        pub_year = ""
        pub_date = ""
        
        if a_date:
            a_date_str = str(a_date)
            pub_year = a_date_str[:4] if len(a_date_str) >= 4 else ""
            pub_date = a_date_str  # 完整日期 "2015-06-11"
            logger.info(f"找到 aDate: {a_date}")
        else:
            logger.warning("未找到 aDate 字段")
        
        return {
            "albumname": album_info.get("albumname"),
            "singername": album_info.get("singername"),
            "pub_time": a_date,        # 保存原始日期
            "pub_year": pub_year,       # 提取的年份
            "pub_date": pub_date,       # 完整日期
            "genre": album_info.get("genre"),
            "language": album_info.get("language"),
            "desc": album_info.get("desc")
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"获取专辑信息超时：{albummid}")
        return None
    except Exception as e:
        logger.error(f"获取专辑信息异常 {albummid}: {e}")
        return None
```

#### 1.2 新增方法：`download_cover_data()`

```python
def download_cover_data(self, albummid: str, size: str = "500x500") -> Optional[bytes]:
    """
    下载专辑封面数据
    
    Args:
        albummid: 专辑 ID
        size: 图片尺寸
    
    Returns:
        bytes: 封面图片数据，失败返回 None
    """
    try:
        # 方式1：使用 API
        image_url = self.get_album_cover_url(albummid, size)
        
        if not image_url:
            # 方式2：使用直接 URL
            image_url = f"http://i.gtimg.cn/music/photo/mid_album_500/7/a/{albummid}.jpg"
            logger.warning(f"API 获取封面失败，使用直接 URL: {image_url}")
        
        logger.info(f"下载封面: {image_url}")
        
        # 下载图片
        response = self.session.get(image_url, timeout=self.timeout)
        response.raise_for_status()
        
        cover_data = response.content
        logger.info(f"封面数据大小: {len(cover_data)} bytes")
        return cover_data
        
    except Exception as e:
        logger.error(f"下载封面失败 {albummid}: {e}")
        return None
```

#### 1.3 修改方法：`get_album_metadata_cached()`

**修改前**：
```python
# 使用错误的字段
album_info = api_client.get_album_info(albummid)
pub_year = album_info.get("pub_year", "")
```

**修改后**：
```python
# 使用正确的新方法
album_info = api_client.get_album_info_with_date(albummid)
if not album_info:
    return None

# 从新的响应结构中提取年份和日期
pub_year = album_info.get("pub_year", "")
pub_date = album_info.get("pub_date", "")

# 下载封面数据
cover_data = api_client.download_cover_data(albummid, size="500x500")

# 构建返回数据
metadata = {
    "albummid": albummid,
    "artist": search_result.get("singername"),
    "album": search_result.get("albumname"),
    "pub_year": pub_year,
    "pub_date": pub_date,
    "genre": album_info.get("genre"),
    "language": album_info.get("language"),
    "cover_data": cover_data,
    "cover_url": image_url  # 从 download_cover_data 返回
}
```

### 方案 2：创建独立补充脚本

**文件**：`supplement_album_metadata.py`

**功能设计**：

#### 2.1 核心功能

1. **扫描目录**
   - 支持根目录（批量处理多个专辑）
   - 支持单个专辑目录
   - 自动识别所有子目录作为专辑

2. **读取元数据**
   - 从 FLAC 文件读取 ARTIST 和 ALBUM 标签
   - 提取音轨号（如果需要）

3. **调用 API**
   - 搜索专辑获取 albummid
   - 调用 getAlbumInfo 获取 aDate
   - 下载专辑封面

4. **嵌入元数据**
   - 添加 DATE 字段（年份）
   - 嵌入封面图片到 FLAC 文件
   - 保存 cover.jpg 到专辑目录

5. **缓存机制**
   - 基于 ARTIST::ALBUM 的缓存键
   - 避免同一专辑重复调用 API

#### 2.2 处理流程

```
扫描目录
   ├─ 找到所有子目录（专辑）
   ├─ 找到每个子目录中的 FLAC 文件
   └─ 按专辑分组处理

处理每个专辑
   ├─ 从第一个 FLAC 文件读取标签
   ├─ 获取 ARTIST 和 ALBUM
   ├─ 检查缓存
   │   ├─ 命中 → 使用缓存数据
   │   └─ 未命中 → 调用 API
   ├─ 获取专辑信息（包含 aDate）
   ├─ 下载封面
   ├─ 为所有 FLAC 文件嵌入元数据
   └─ 保存 cover.jpg

完成
   ├─ 显示统计信息
   ├─ 保存处理日志
   └─ 返回成功/失败状态
```

#### 2.3 参数说明

```bash
# 基本用法
python supplement_album_metadata.py --input "G:\QQMusic\Decrypted"

# 详细输出
python supplement_album_metadata.py --input "G:\QQMusic\Decrypted" --verbose

# 指定专辑
python supplement_album_metadata.py --input "G:\QQMusic\Decrypted\周杰伦 - 叶惠美"
```

**CLI 参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input`, `-i` | 输入目录路径 | 必需 |
| `--verbose`, `-v` | 详细输出 | False |
| `--help`, `-h` | 显示帮助信息 | - |

### 方案 3：修改 GUI 自动获取

**文件**：`gui_backup/main_gui.py`

**修改位置**：`add_flac_metadata()` 方法

**修改内容**：

```python
def add_flac_metadata(self, flac_file_path):
    """
    为 FLAC 文件添加元数据（音轨号、封面、发行年份）
    
    Args:
        flac_file_path (str): FLAC 文件路径
    """
    try:
        filename = os.path.basename(flac_file_path)
        
        # 步骤1：添加音轨号
        track_number = extract_track_number_from_filename(filename)
        
        if track_number is not None:
            success = add_track_number_to_flac(flac_file_path, track_number)
            if success:
                self.log(f"✓ 已添加音轨号 {track_number}")
            else:
                self.log(f"✗ 添加音轨号失败")
        else:
            self.log(f"未找到音轨号，跳过音轨号添加")
        
        # 步骤2：获取并添加专辑元数据（使用修复后的 API）
        self.log("获取专辑信息...")
        
        try:
            # 创建 API 客户端（使用修复后的方法）
            api_client = QQMusicAPIClient()
            
            # 读取文件元数据
            flac_tags = get_flac_metadata_tags(flac_file_path)
            artist = flac_tags.get("artist")
            album = flac_tags.get("album")
            
            if artist and album:
                # 搜索专辑
                search_result = api_client.search_album(artist, album)
                if search_result:
                    albummid = search_result.get("albummid")
                    if albummid:
                        # 使用新的方法获取专辑信息（包含 aDate）
                        album_info = api_client.get_album_info_with_date(albummid)
                        if album_info:
                            # 提取年份和日期
                            pub_year = album_info.get("pub_year", "")
                            pub_date = album_info.get("pub_date", "")
                            a_date = album_info.get("pub_time", "")
                            
                            # 显示信息
                            if pub_year:
                                self.log(f"发行年份: {pub_year}")
                            if pub_date:
                                self.log(f"发行日期: {pub_date}")
                            
                            # 下载封面
                            self.log("下载专辑封面...")
                            cover_data = api_client.download_cover_data(albummid)
                            
                            if cover_data:
                                self.log("✓ 封面下载成功")
                                
                                # 嵌入元数据
                                audio = FLAC(flac_file_path)
                                audio.clear_pictures()
                                
                                # 添加年份
                                if pub_year:
                                    audio["DATE"] = pub_year
                                
                                # 添加封面
                                image = Picture()
                                image.type = 3
                                image.mime = "image/jpeg"
                                image.data = cover_data
                                audio.add_picture(image)
                                
                                # 保存
                                audio.save()
                                
                                self.log("✓ 已嵌入封面和年份")
                                
                                # 保存封面文件
                                album_dir = os.path.dirname(flac_file_path)
                                cover_path = os.path.join(album_dir, "cover.jpg")
                                os.makedirs(album_dir, exist_ok=True)
                                
                                with open(cover_path, 'wb') as f:
                                    f.write(cover_data)
                                
                                self.log(f"✓ 已保存封面: cover.jpg")
                            else:
                                self.log("✗ 封面下载失败")
                        else:
                            self.log("✗ 未找到 albummid")
                    else:
                        self.log("✗ 未找到专辑")
                else:
                    self.log("✗ 缺少必要的标签 (ARTIST 或 ALBUM)")
            else:
                self.log("✗ 缺少必要的标签 (ARTIST 或 ALBUM)")
                
        except Exception as e:
            self.log(f"添加元数据异常: {e}")
    
    except Exception as e:
        self.log(f"处理异常 {filename}: {e}")
```

---

## 📂 文件变更总结

### 新建文件（1 个）

| 文件 | 行数 | 说明 |
|------|------|------|
| `supplement_album_metadata.py` | ~350 | 独立补充脚本 |

### 修改文件（2 个）

| 文件 | 修改内容 | 说明 |
|------|---------|------|
| `qqmusic_api_client.py` | +80 行 | 新增 `get_album_info_with_date()` 和 `download_cover_data()` 方法 |
| `gui_backup/main_gui.py` | +60 行 | 更新 `add_flac_metadata()` 方法使用新的 API |

**总计**：~490 行新代码

---

## 🎯 实施步骤

### 步骤 1：修复 API 调用（qqmusic_api_client.py）

1. 在 `QQMusicAPIClient` 类中添加 `get_album_info_with_date()` 方法
2. 在 `QQMusicAPIClient` 类中添加 `download_cover_data()` 方法
3. 更新 `get_album_metadata_cached()` 函数调用新方法
4. 测试 API 调用是否能正确获取 aDate

**预期结果**：
- ✅ 能正确从 API 获取 aDate 字段
- ✅ 能正确提取年份 "2015"
- ✅ 能正确提取日期 "2015-06-11"

### 步骤 2：创建独立补充脚本（supplement_album_metadata.py）

1. 创建完整的脚本文件
2. 实现所有核心功能
3. 添加 CLI 参数解析
4. 实现详细的日志输出
5. 实现进度显示和统计

**预期结果**：
- ✅ 能扫描指定目录下的所有专辑
- ✅ 能为每个专辑补充封面和年份
- ✅ 支持批量处理多个专辑
- ✅ 提供详细的处理日志

### 步骤 3：修改 GUI 自动获取（gui_backup/main_gui.py）

1. 更新 `add_flac_metadata()` 方法
2. 集成新的 API 调用方式
3. 添加详细的日志输出
4. 确保错误隔离（失败不影响解密）

**预期结果**：
- ✅ 解密完成后自动获取专辑信息
- ✅ 自动添加年份和封面到 FLAC 文件
- ✅ 自动保存 cover.jpg
- ✅ 显示详细的处理日志

---

## 🧪 测试计划

### 测试 1：API 修复测试

```bash
# 测试新的 API 调用
cd D:\WorkDev\qqmusic_decryptor
python -c "
from qqmusic_api_client import QQMusicAPIClient

api = QQMusicAPIClient()
albummid = '000ILKG63fED7K'

# 测试新方法
result = api.get_album_info_with_date(albummid)
if result:
    print(f'  albumname: {result.get(\"albumname\")}')
    print(f'  aDate: {result.get(\"pub_time\")}')
    print(f'  pub_year: {result.get(\"pub_year\")}')
    print(f'  pub_date: {result.get(\"pub_date\")}')
else:
    print('获取失败')
"
```

**预期输出**：
```
  albumname: Never Odd Or Even
  aDate: 2015-06-11
  pub_year: 2015
  pub_date: 2015-06-11
```

### 测试 2：独立脚本测试

```bash
# 测试单个专辑
python supplement_album_metadata.py --input "G:\QQMusic\Decrypted\周杰伦 - 叶惠美"

# 测试根目录（批量处理）
python supplement_album_metadata.py --input "G:\QQMusic\Decrypted" --verbose
```

**预期输出**：
```
============================================================
  专辑元数据补充工具
============================================================
目标路径: G:\QQMusic\Decrypted\周杰伦 - 叶惠美
覆盖策略: 都覆盖

[INFO] 扫描目录...
[INFO] 找到 1 个 FLAC 文件

[INFO] 专辑信息: 周杰伦 - 叶惠美
[INFO] 找到 aDate: 2015-06-11
[INFO] 下载专辑封面...
[INFO] ✓ 封面下载成功
[INFO] 发行年份: 2015
[INFO] ✓ 已添加音轨号 1
[INFO] ✓ 已嵌入封面和年份
[INFO] ✓ 已保存封面: cover.jpg

============================================================
  处理完成
============================================================
总专辑数: 1
总文件数: 1
成功: 1
失败: 0
跳过: 0
耗时: 3.25 秒
============================================================
```

### 测试 3：GUI 自动获取测试

1. 启动 frida-server（管理员权限）
2. 启动 QQ Music 并登录 VIP
3. 启动 GUI：`run_gui_simple.bat`
4. 配置路径并开始解密
5. 观察日志窗口中的处理信息

**预期输出**：
```
[INFO] 正在解密: 01 歌曲.flac
[INFO] ✓ 解密成功: 01 歌曲.flac
[INFO] ✓ 已添加音轨号 1
[INFO] 获取专辑信息...
[INFO] 专辑信息: 周杰伦 - 叶惠美
[INFO] 找到 aDate: 2015-06-11
[INFO] 发行年份: 2015
[INFO] 下载专辑封面...
[INFO] ✓ 封面下载成功
[INFO] ✓ 已嵌入封面和年份
[INFO] ✓ 已保存封面: cover.jpg
[INFO] ✓ 已复制歌词文件
```

---

## 📊 成功标准

### API 修复成功标准

- ✅ `get_album_info_with_date()` 能正确获取 aDate
- ✅ `pub_year` 正确提取年份 "2015"
- ✅ `pub_date` 正确提取日期 "2015-06-11"
- ✅ 返回数据结构正确

### 独立脚本成功标准

- ✅ 能扫描指定目录
- ✅ 能正确读取 FLAC 文件标签
- ✅ 能正确调用修复后的 API
- ✅ 能正确嵌入年份到 FLAC
- ✅ 能正确嵌入封面到 FLAC
- ✅ 能正确保存 cover.jpg
- ✅ 日志输出清晰详细
- ✅ 统计信息准确

### GUI 自动获取成功标准

- ✅ 解密完成后自动调用 API
- ✅ 年份成功写入 FLAC 文件
- ✅ 封面成功嵌入 FLAC 文件
- ✅ cover.jpg 成功保存
- ✅ 日志信息显示在 GUI 窗口
- ✅ 错误不影响解密流程

---

## 📝 注意事项

### API 调用注意

- **字段名**：必须使用 `aDate`（注意大小写）
- **数据来源**：从 `data["response"]["data"]` 层级获取
- **错误处理**：API 失败时有降级方案

### 独立脚本注意

- **权限要求**：需要读写 FLAC 文件的权限
- **网络要求**：需要访问 API 服务
- **覆盖策略**：默认都覆盖，避免残留数据
- **缓存机制**：使用内存缓存，重启后清空

### GUI 集成注意

- **异步处理**：不要阻塞 GUI 主线程
- **错误隔离**：元数据处理失败不影响解密结果
- **日志输出**：使用 GUI 的日志窗口，不是控制台
- **用户体验**：显示进度，允许取消操作

---

## 🚀 下一步行动

1. ✅ **创建实施计划文档**（当前任务）
2. ⏳ **修复 API 调用**（qqmusic_api_client.py）
3. ⏳ **创建独立脚本**（supplement_album_metadata.py）
4. ⏳ **修改 GUI 自动获取**（gui_backup/main_gui.py）
5. ⏳ **测试所有功能**
6. ⏳ **更新文档**

---

**文档创建时间**：2026-01-29
**文档版本**：v1.0
**状态**：✅ 待实施
