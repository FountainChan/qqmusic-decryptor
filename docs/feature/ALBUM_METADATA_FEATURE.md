# 封面和发行年份功能实现文档

## 功能概述

在解密音乐成功后，自动为 FLAC 文件添加以下元数据：

1. **音轨号**：从文件名提取并写入 TRACKNUMBER
2. **发行年份**：从 QQ Music API 获取并写入 DATE
3. **专辑封面**：从 QQ Music API 下载并嵌入到 FLAC 文件
4. **封面文件**：在专辑目录保存为 cover.jpg

## 实现方案

### 技术架构

```
解密成功
   ↓
提取音轨号（从文件名）
   ↓
获取 FLAC 元数据（ARTIST、ALBUM）
   ↓
调用 QQ Music API
   ├─ 搜索专辑（getSearchByKey）
   ├─ 获取专辑信息（getAlbumInfo）
   └─ 下载封面（getImageUrl）
   ↓
处理元数据
   ├─ 添加音轨号到 FLAC
   ├─ 添加发行年份到 FLAC
   ├─ 嵌入封面到 FLAC
   └─ 保存封面为 cover.jpg
   ↓
保存 FLAC 文件
```

### 核心模块

#### 1. QQ Music API 客户端（qqmusic_api_client.py）

**主要类和方法**：

```python
class QQMusicAPIClient:
    """QQ音乐 API 客户端"""
    
    def search_album(artist, album_name):
        """搜索专辑获取 albummid"""
    
    def get_album_info(albummid):
        """获取专辑详细信息（包含发行年份）"""
    
    def get_album_cover_url(albummid, size="500x500"):
        """获取专辑封面 URL"""
    
    def download_album_cover(albummid, dest_path):
        """下载专辑封面到指定路径"""


class AlbumMetadataCache:
    """专辑元数据缓存，避免重复请求"""
    
    def get(key):
        """从缓存获取专辑信息"""
    
    def set(key, data):
        """设置缓存"""
```

**API 端点**：

| 功能 | 端点 | 参数 |
|------|------|------|
| 搜索专辑 | `/getSearchByKey` | key, remoteplace=album, page, limit |
| 专辑信息 | `/getAlbumInfo` | albummid |
| 获取封面 | `/getImageUrl` | id, size |

#### 2. 元数据处理工具（metadata_utils.py）

**新增函数**：

```python
def embed_cover_to_flac(flac_file_path, cover_data, metadata=None):
    """将封面嵌入到 FLAC 文件"""

def get_flac_metadata_tags(flac_file_path):
    """获取 FLAC 文件的元数据标签（ARTIST、ALBUM、TITLE）"""

def save_cover_to_directory(album_dir, cover_data):
    """保存封面图片到专辑目录（cover.jpg）"""

def process_album_metadata(flac_file_path, api_client=None, use_cache=True):
    """处理 FLAC 文件的专辑元数据（封面、发行年份）"""
```

**缓存机制**：

- **基于 ARTIST + ALBUM 的缓存键**
- **避免同一专辑重复请求 API**
- **同一专辑目录下所有歌曲共享封面和日期**

#### 3. 集成到主程序

**CLI 版本（main_cli.py）**：

```python
class QQMusicDecryptorCLI:
    def add_flac_metadata(self, flac_file_path):
        """
        添加完整的元数据：
        1. 音轨号
        2. 发行年份
        3. 专辑封面
        """
        # 步骤1：添加音轨号
        track_number = extract_track_number_from_filename(filename)
        add_track_number_to_flac(flac_file_path, track_number)
        
        # 步骤2：处理专辑元数据
        api_client = QQMusicAPIClient()
        result = process_album_metadata(flac_file_path, api_client)
        
        # 步骤3：显示结果
        if result['success']:
            metadata = result.get('metadata')
            pub_year = metadata.get('pub_year')
            if pub_year:
                self.log(f"✓ 已添加发行年份 {pub_year}")
            
            if metadata.get('cover_data'):
                self.log("✓ 已嵌入封面到文件")
                self.log("✓ 已保存封面到 cover.jpg")
```

**GUI 版本（gui_backup/main_gui.py）**：

```python
class QQMusicDecryptorGUI:
    def add_flac_metadata(self, flac_file_path):
        """
        GUI 版本的元数据处理
        实现与 CLI 版本相同的功能
        """
        # 实现逻辑与 CLI 版本相同
        # 使用 self.log() 输出日志
```

### 工作流程

#### 详细步骤

1. **解密完成**
   - Frida hook 解密成功
   - 文件重命名为最终文件名

2. **添加音轨号**
   - 从文件名提取数字前缀
   - 写入 FLAC 文件的 TRACKNUMBER 字段

3. **读取文件元数据**
   - 从 FLAC 文件读取 ARTIST、ALBUM 标签
   - 用于后续 API 查询

4. **查询 QQ Music API**
   - 使用 ARTIST + ALBUM 搜索专辑
   - 获取 albummid、pub_year 等信息
   - 下载封面图片数据

5. **处理封面**
   - 将封面图片嵌入 FLAC 文件
   - 在专辑目录保存为 cover.jpg

6. **添加发行年份**
   - 将 pub_year 写入 FLAC 文件的 DATE 字段

7. **完成**
   - 保存 FLAC 文件
   - 显示处理结果

### 缓存策略

#### 为什么需要缓存？

- **节省资源**：同一专辑多首歌，只需查询一次 API
- **提高速度**：避免重复网络请求
- **减少服务器压力**：降低 API 调用频率

#### 缓存键生成

```python
cache_key = f"{artist}::{album}"
```

#### 缓存内容

```python
{
    "albummid": "000MkMni19ClKG",
    "artist": "周杰伦",
    "album": "叶惠美",
    "pub_year": "2003",
    "pub_date": "2003-07-31",
    "genre": "流行",
    "language": "国语",
    "cover_data": bytes,  # 封面图片二进制数据
    "cover_url": "https://y.gtimg.cn/..."
}
```

### API 配置

**基础 URL**：

```
http://192.168.110.194:3200
```

**请求超时**：

- 默认：10 秒
- 可在 QQMusicAPIClient 初始化时自定义

**封面尺寸选项**：

| 尺寸 | 说明 | 文件大小 |
|------|------|----------|
| 300x300 | 默认，适合小图 | ~50KB |
| 500x500 | 推荐，平衡质量和大小 | ~150KB |
| 800x800 | 高清，适合大图 | ~400KB |
| 1000x1000 | 超高清，文件较大 | ~800KB |

### 文件位置

#### 专辑封面文件

**路径**：`{专辑目录}/cover.jpg`

**示例**：

```
G:\QQMusic\Decrypted\VipSongsDownload\
└── 周杰伦 - 叶惠美\
    ├── 01 以父之名.flac
    ├── 02 爷在西元前.flac
    ├── ...
    └── cover.jpg  ← 专辑封面
```

#### 同专辑共享

```
专辑 A 目录/
├── 01 歌曲1.flac  ← 使用相同的 cover.jpg 和 pub_year
├── 02 歌曲2.flac  ← 使用相同的 cover.jpg 和 pub_year
├── 03 歌曲3.flac  ← 使用相同的 cover.jpg 和 pub_year
└── cover.jpg
```

## 依赖管理

### 新增依赖

```
requests>=2.31.0
```

### 安装命令

```bash
pip install requests
```

### 更新 requirements.txt

```txt
frida==16.7.10
mutagen>=1.47.0
requests>=2.31.0
```

## 功能特性

### 核心特性

- ✅ 自动从文件名提取音轨号
- ✅ 从 QQ Music API 获取专辑信息
- ✅ 下载专辑封面并嵌入 FLAC
- ✅ 在专辑目录保存封面（cover.jpg）
- ✅ 添加发行年份到 FLAC 元数据
- ✅ 智能缓存避免重复请求
- ✅ 错误处理不影响解密流程

### 优化特性

- ✅ 同一专辑多首歌共享封面和年份
- ✅ 支持多种封面尺寸
- ✅ API 失败时有降级策略
- ✅ 详细的日志记录

### 兼容性

- ✅ 完全向后兼容现有功能
- ✅ 不影响歌词文件复制
- ✅ 不影响目录结构保留
- ✅ 支持批量处理

## 错误处理

### 常见错误及处理

| 错误类型 | 处理方式 | 日志级别 |
|---------|---------|---------|
| API 连接失败 | 跳过封面和年份 | WARNING |
| 搜索无结果 | 跳过封面和年份 | WARNING |
| 下载封面失败 | 跳过封面，保留年份 | WARNING |
| 封面文件已存在 | 跳过下载，使用缓存 | INFO |
| 缺少元数据标签 | 跳过处理 | DEBUG |

### 错误隔离

所有错误都使用 try-except 捕获，确保：

1. 不影响解密流程
2. 音轨号添加失败不影响封面下载
3. 封面下载失败不影响年份添加
4. 所有错误都记录到日志

## 性能优化

### 当前性能

| 操作 | 首次处理 | 缓存命中 |
|------|---------|---------|
| API 查询 | 1-2秒 | 0秒 |
| 封面下载 | 1-3秒 | 0秒 |
| 元数据写入 | <1秒 | <1秒 |
| 总计 | 3-6秒 | <1秒 |

### 性能指标

- **单文件处理**：首次 3-6秒，缓存命中 <1秒
- **同专辑多文件**：第一首 3-6秒，后续 <1秒
- **API 调用次数**：同专辑 N 首歌仅调用 1 次

## 测试

### 测试脚本

创建 `test_new_features.py` 测试新功能：

```bash
python test_new_features.py
```

### 测试内容

1. ✅ API 连接测试
2. ✅ 搜索专辑功能
3. ✅ 获取专辑信息
4. ✅ 获取封面 URL
5. ✅ 元数据处理函数
6. ✅ 文件名解析
7. ✅ 完整流程测试

### 测试结果

```
============================================================
  封面和发行年份功能测试
============================================================

测试 API 连接...
✓ 搜索成功
  专辑名: 叶惠美
  歌手: 周杰伦
  albummid: 000MkMni19ClKG

测试获取专辑信息...
✓ 获取专辑信息成功
  发行年份: 2003
  发行日期: 2003-07-31
  类型: 流行

测试获取封面 URL...
✓ 获取封面 URL 成功
  URL: https://y.gtimg.cn/...

============================================================
  测试总结
============================================================
API 连接: ✓ 通过
元数据函数: ✓ 通过

✓ 所有测试通过！
```

## 使用示例

### CLI 版本

```bash
# 自动处理（推荐）
python main_cli.py

# 输出示例
[INFO] ✓ 解密成功: 01 以父之名.flac
[INFO] ✓ 已添加音轨号 1
[INFO] 获取专辑信息...
[INFO] 发行年份: 2003
[INFO] ✓ 已添加发行年份 2003
[INFO] ✓ 已嵌入封面到文件
[INFO] ✓ 已保存封面到 cover.jpg
```

### GUI 版本

1. 启动 GUI：`run_gui_simple.bat`
2. 配置输入/输出目录
3. 点击"开始解密"
4. 查看日志窗口的进度信息

### 预期结果

解密后的 FLAC 文件包含：

- **音轨号**：TRACKNUMBER=1
- **发行年份**：DATE=2003
- **专辑封面**：内嵌图片
- **封面文件**：cover.jpg 在专辑目录

## 文件变更

### 新建文件

| 文件 | 说明 | 行数 |
|------|------|------|
| `qqmusic_api_client.py` | QQ Music API 客户端 | ~280 |
| `test_new_features.py` | 功能测试脚本 | ~150 |

### 修改文件

| 文件 | 修改内容 | 变更 |
|------|---------|------|
| `metadata_utils.py` | 新增元数据处理函数 | +150行 |
| `main_cli.py` | 更新 add_flac_metadata 方法 | +30行 |
| `gui_backup/main_gui.py` | 更新 add_flac_metadata 方法 | +25行 |
| `requirements.txt` | 添加 requests 依赖 | +1行 |

### 总计

- **新建文件**：2 个
- **修改文件**：4 个
- **新增代码**：~430 行

## 注意事项

### API 依赖

- ⚠️ 必须确保 QQ Music API 服务可访问
- ⚠️ API 地址：http://192.168.110.194:3200
- ⚠️ API 响应超时：10 秒（可配置）

### 网络要求

- ⚠️ 需要网络连接访问 API
- ⚠️ 需要稳定的网络环境
- ⚠️ 网络慢会影响封面下载速度

### 元数据依赖

- ⚠️ FLAC 文件必须包含 ARTIST 和 ALBUM 标签
- ⚠️ 如果缺少标签，跳过封面和年份处理
- ⚠️ 可以手动编辑 FLAC 文件添加标签

### 缓存管理

- ⚠️ 缓存存储在内存中
- ⚠️ 程序重启后缓存清空
- ⚠️ 可考虑使用持久化缓存（SQLite）

## 未来改进

### 可能的优化方向

1. **持久化缓存**
   - 使用 SQLite 存储缓存
   - 避免重启后重新查询

2. **并发下载**
   - 使用多线程并发下载封面
   - 提高批量处理速度

3. **智能降级**
   - API 失败时尝试其他封面来源
   - 如：iTunes、MusicBrainz

4. **封面质量选择**
   - 根据文件大小自动选择封面尺寸
   - 小文件使用小封面，大文件使用高清封面

5. **重试机制**
   - API 请求失败时自动重试
   - 使用指数退避策略

## 参考文档

- **API 文档**：`D:\WorkDev\QQMusicCodes\qq-music-api\docs\api-album-guide.md`
- **封面查找逻辑**：`D:\WorkDev\get_cover_art\docs\封面查找逻辑分析.md`
- **get_cover_art 项目**：封面下载和嵌入实现参考

## 总结

新功能实现了完整的专辑元数据处理：

✅ **音轨号**：从文件名提取并写入
✅ **发行年份**：从 QQ Music API 获取并写入
✅ **专辑封面**：从 QQ Music API 下载并嵌入
✅ **封面文件**：保存为 cover.jpg
✅ **智能缓存**：同专辑多首歌共享信息
✅ **错误隔离**：失败不影响解密流程
✅ **完整集成**：CLI 和 GUI 版本都已集成

功能已完全实现并集成到项目中，可以开始使用。

---

**文档创建时间**：2026-01-29
**功能版本**：v1.0
