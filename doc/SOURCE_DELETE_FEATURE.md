# 源文件和空目录删除功能 - 开发文档

## 1. 需求说明

### 功能描述

在 mflac/mgg 文件转换成功且歌词复制完成后，自动删除源文件和（可选的）空目录。

**关键规则**：
- ✅ 只在转换成功后执行删除
- ✅ 歌词复制只执行，不关心结果（copy_lyrics_file 无需修改）
- ✅ 删除源音频文件（.mflac/.mgg）
- ✅ 删除源歌词文件时只检查源文件是否存在，不验证复制结果
- ✅ 递归删除空目录，直到到达输入根目录
- ✅ 添加删除统计信息（删除的文件数和目录数）
- ✅ GUI 提供控制选项
- ✅ 配置文件提供控制选项和默认路径

### 用户确认的设计决策

| 选项 | 选择 | 说明 |
|------|------|------|
| 歌词复制验证 | ✅ 不验证 | 只执行，不关心复制结果 |
| 删除歌词文件 | ✅ 简单删除 | 只检查源文件是否存在，不验证复制结果 |
| 默认删除源文件 | ✅ 默认启用 | 默认删除源文件 |
| 默认删除空目录 | ✅ 默认启用 | 默认删除空目录 |
| GUI 默认路径 | ✅ 从 config.ini 读取 | 使用 config.ini 的 PATHS 配置（VipSongsDownload 路径） |
| 添加统计信息 | ✅ 添加统计 | 记录删除的文件数和目录数 |

### 输入输出示例

**输入**:
```
G:\QQMusic\Download\VipSongsDownload\歌手\专辑\
├── 歌曲.mflac    ← 要删除
├── 歌曲.lrc      ← 要删除
└── 其他.mflac    ← 未处理，保留
```

**转换后**:
```
G:\QQMusic\Download\VipSongsDownload\歌手\专辑\
└── 其他.mflac    ← 保留

G:\QQMusic\Decrypted\VipSongsDownload\歌手\专辑\
├── 歌曲.flac    ← 解密成功
└── 歌曲.lrc     ← 复制成功
```

**目录为空时**:
```
G:\QQMusic\Download\VipSongsDownload\歌手\专辑\  ← 目录为空，删除
G:\QQMusic\Download\VipSongsDownload\歌手\      ← 目录为空，删除
G:\QQMusic\Download\VipSongsDownload\            ← 目录不为空，停止
```

### 处理逻辑

```
对于每个加密文件：
    1. 解密音频文件
    2. 如果解密成功：
        a. 重命名临时文件
        b. 验证文件完整性
        c. 添加元数据（仅 FLAC）
        d. 复制歌词文件
        e. 删除源文件和歌词文件
        f. 删除空目录（递归）
        g. 记录成功日志
    3. 如果解密失败：
        - 不执行任何删除操作
```

---

## 2. 配置设计

### config.ini 配置文件

```ini
[PATHS]
# GUI 默认路径（包含 VipSongsDownload 后缀）
input_dir = G:\QQMusic\Download\VipSongsDownload
output_dir = G:\QQMusic\Decrypted\VipSongsDownload

[LOGGING]
log_level = INFO
log_file = logs/decrypt.log
save_stats = true

[OPTIONS]
preserve_structure = true
skip_existing = true
max_retries = 3
retry_delay = 2
verify_metadata = true
# 删除功能配置
delete_source = true              # 是否删除源文件（默认启用）
delete_empty_dirs = true          # 是否删除空目录（默认启用）
delete_lyrics = true              # 是否同时删除歌词文件（默认启用）
```

**配置说明**：
- `[PATHS]` 部分：提供 CLI 和 GUI 的默认路径
  - GUI 启动时从该配置读取默认值
  - CLI 可通过命令行参数覆盖
- `[OPTIONS]` 部分：新增 3 个删除相关配置项
  - CLI 从配置文件读取
  - GUI 使用界面控件，但从配置文件读取初始默认值

### GUI 新增界面控件

在 `gui_backup/main_gui.py` 中添加三个复选框：

```python
# 第 46 行附近添加变量
self.delete_source_var = tk.BooleanVar(value=True)
self.delete_empty_dirs_var = tk.BooleanVar(value=True)
self.delete_lyrics_var = tk.BooleanVar(value=True)

# 在"选项"部分添加复选框（约第 80 行）
ttk.Checkbutton(
    options_frame,
    text="转换后删除源文件",
    variable=self.delete_source_var
).grid(row=0, column=0, sticky=tk.W, pady=2)

ttk.Checkbutton(
    options_frame,
    text="删除空目录",
    variable=self.delete_empty_dirs_var
).grid(row=1, column=0, sticky=tk.W, pady=2)

ttk.Checkbutton(
    options_frame,
    text="同时删除歌词文件",
    variable=self.delete_lyrics_var
).grid(row=2, column=0, sticky=tk.W, pady=2)
```

---

## 3. 代码实现

### CLI 版本 (main_cli.py)

#### 3.1 导入模块（第 11 行附近）

**无需修改** - 已有 `import os`

#### 3.2 初始化统计变量（第 50-60 行左右）

```python
# 在 __init__ 方法中添加
self.deleted_files = 0       # 删除的文件数统计
self.deleted_dirs = 0        # 删除的目录数统计
```

#### 3.3 新增方法 - 删除源文件（第 256 行之后）

```python
def delete_source_file(self, input_file, delete_lyrics=False):
    """
    删除源文件和（可选的）歌词文件

    Args:
        input_file: 输入文件的完整路径
        delete_lyrics: 是否同时删除歌词文件

    Returns:
        int: 删除的文件数量
    """
    deleted_count = 0

    try:
        # 删除源文件
        if os.path.exists(input_file):
            os.remove(input_file)
            deleted_count += 1
            self.log(f"✓ 已删除源文件: {os.path.basename(input_file)}", "INFO")

        # 删除歌词文件（如果启用）
        if delete_lyrics:
            lyric_file = os.path.splitext(input_file)[0] + ".lrc"
            if os.path.exists(lyric_file):
                os.remove(lyric_file)
                deleted_count += 1
                self.log(f"✓ 已删除歌词文件: {os.path.basename(lyric_file)}", "INFO")

    except Exception as e:
        self.log(f"删除文件失败: {e}", "WARNING")

    return deleted_count
```

#### 3.4 新增方法 - 删除空目录（第 260 行之后）

```python
def cleanup_empty_dirs(self, dir_path, root_dir):
    """
    递归删除空目录，直到 root_dir

    Args:
        dir_path: 要检查的目录路径
        root_dir: 根目录（停止删除的边界）

    Returns:
        int: 删除的目录数量
    """
    deleted_count = 0

    # 规范化路径
    dir_path = os.path.normpath(dir_path)
    root_dir = os.path.normpath(root_dir)

    # 如果已经到达根目录或超出范围，停止
    if dir_path == root_dir or not dir_path.startswith(root_dir):
        return deleted_count

    try:
        # 检查目录是否为空
        if os.path.exists(dir_path) and not os.listdir(dir_path):
            os.rmdir(dir_path)
            deleted_count += 1
            self.log(f"✓ 已删除空目录: {dir_path}", "INFO")

            # 递归删除父目录
            parent_dir = os.path.dirname(dir_path)
            deleted_count += self.cleanup_empty_dirs(parent_dir, root_dir)

    except Exception as e:
        self.log(f"删除目录失败: {e}", "WARNING")

    return deleted_count
```

#### 3.5 修改 decrypt_file 方法（第 360 行附近）

**原始代码（第 332-363 行）**:
```python
if "Success" in result:
    # 重命名为最终文件名
    os.rename(temp_file_path, output_file)

    # 验证输出文件
    if output_file.lower().endswith('.flac'):
        if not self.verify_flac_file(output_file):
            os.remove(output_file)
            self.log("FLAC验证失败，删除文件", "ERROR")
            raise Exception("FLAC validation failed")

    # 检查输出文件大小
    ...

    if output_file.lower().endswith('.flac'):
        self.add_flac_metadata(output_file)

    self.copy_lyrics_file(input_file, output_file)

    self.log(f"✓ 解密成功: {os.path.basename(output_file)}", "INFO")
    return "success"
```

**修改后（添加删除逻辑）**:
```python
if "Success" in result:
    # 重命名为最终文件名
    os.rename(temp_file_path, output_file)

    # 验证输出文件
    if output_file.lower().endswith('.flac'):
        if not self.verify_flac_file(output_file):
            os.remove(output_file)
            self.log("FLAC验证失败，删除文件", "ERROR")
            raise Exception("FLAC validation failed")

    # 检查输出文件大小
    ...

    if output_file.lower().endswith('.flac'):
        self.add_flac_metadata(output_file)

    # 复制歌词文件
    self.copy_lyrics_file(input_file, output_file)

    # === 新增：删除源文件和空目录 ===
    if self.delete_source:
        # 删除源文件和歌词文件
        deleted_count = self.delete_source_file(input_file, self.delete_lyrics)
        self.deleted_files += deleted_count

        # 删除空目录
        if self.delete_empty_dirs:
            file_dir = os.path.dirname(input_file)
            deleted_dirs = self.cleanup_empty_dirs(file_dir, self.input_dir)
            self.deleted_dirs += deleted_dirs
    # ===============================

    self.log(f"✓ 解密成功: {os.path.basename(output_file)}", "INFO")
    return "success"
```

#### 3.6 修改 save_stats 方法（第 520 行附近）

```python
# 在 save_stats 方法中添加删除统计
def save_stats(self, stats):
    """保存统计信息到JSON文件"""
    stats["cleanup"] = {
        "deleted_files": self.deleted_files,
        "deleted_dirs": self.deleted_dirs
    }

    # 原有保存逻辑...
    os.makedirs(os.path.dirname(stats_file), exist_ok=True)
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
```

#### 3.7 修改配置读取（第 54-84 行附近）

```python
def load_config(self, config_file='config.ini'):
    """加载配置文件"""
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')

        # 读取现有配置...

        # 新增：读取删除配置
        self.delete_source = config.getboolean('OPTIONS', 'delete_source', fallback=True)
        self.delete_empty_dirs = config.getboolean('OPTIONS', 'delete_empty_dirs', fallback=True)
        self.delete_lyrics = config.getboolean('OPTIONS', 'delete_lyrics', fallback=True)
    else:
        # 默认值
        self.delete_source = True
        self.delete_empty_dirs = True
        self.delete_lyrics = True
```

---

### GUI 版本 (gui_backup/main_gui.py)

#### 4.1 导入模块（第 12 行附近）

**需要添加**：
```python
import configparser  # 新增：读取配置文件
```

#### 4.2 添加配置读取方法

在 `__init__` 方法中，在 `setup_ui()` 之前添加配置加载：

```python
def __init__(self, root):
    # ... 其他初始化代码 ...

    # 加载配置文件
    self.load_config()  # 新增

    self.setup_ui()
    self.setup_logging()
    # ...
```

**新增 load_config() 方法**：
```python
def load_config(self):
    """
    加载配置文件
    
    从 config.ini 读取：
    1. 路径配置作为默认值（用于 GUI 默认路径）
    2. 删除选项配置作为默认值
    """
    self.config = configparser.ConfigParser()

    # 默认值（从 config.ini 的 PATHS 部分）
    default_input_dir = "G:\\QQMusic\\Download\\VipSongsDownload"
    default_output_dir = "G:\\QQMusic\\Decrypted\\VipSongsDownload"

    # 默认删除配置
    default_delete_source = True
    default_delete_empty_dirs = True
    default_delete_lyrics = True

    # 读取配置文件
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.ini"
    )

    if os.path.exists(config_path):
        try:
            self.config.read(config_path, encoding='utf-8')

            # 读取路径配置
            if 'PATHS' in self.config:
                default_input_dir = self.config['PATHS'].get('input_dir', default_input_dir)
                default_output_dir = self.config['PATHS'].get('output_dir', default_output_dir)

            # 读取删除配置
            if 'OPTIONS' in self.config:
                default_delete_source = self.config['OPTIONS'].getboolean(
                    'delete_source', fallback=True
                )
                default_delete_empty_dirs = self.config['OPTIONS'].getboolean(
                    'delete_empty_dirs', fallback=True
                )
                default_delete_lyrics = self.config['OPTIONS'].getboolean(
                    'delete_lyrics', fallback=True
                )

            print(f"[配置] 已加载配置文件: {config_path}")
        except Exception as e:
            print(f"[配置] 读取配置文件失败: {e}，使用默认配置")
    else:
        print(f"[配置] 配置文件不存在: {config_path}，使用默认配置")

    # 保存为实例变量，供后续使用
    self.default_input_dir = default_input_dir
    self.default_output_dir = default_output_dir
    self.default_delete_source = default_delete_source
    self.default_delete_empty_dirs = default_delete_empty_dirs
    self.default_delete_lyrics = default_delete_lyrics
```

#### 4.3 初始化变量（第 31 行后附近）

```python
# 状态变量
self.is_processing = False
self.session = None
self.script = None

# 新增：删除选项变量（从配置文件读取默认值）
self.delete_source_var = tk.BooleanVar(value=self.default_delete_source)
self.delete_empty_dirs_var = tk.BooleanVar(value=self.default_delete_empty_dirs)
self.delete_lyrics_var = tk.BooleanVar(value=self.default_delete_lyrics)

# 新增：删除统计变量
self.deleted_files = 0
self.deleted_dirs = 0
```

#### 4.4 设置默认路径（setup_ui 方法第 101 行附近）

```python
# 设置默认路径（从配置文件读取）
self.input_path.set(self.default_input_dir)
self.output_path.set(self.default_output_dir)
```

#### 4.5 新增界面控件（setup_ui 方法第 66 行后）

在"选项"部分添加复选框：

```python
# 选项框架
options_frame = ttk.LabelFrame(main_frame, text="选项")
options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)

# 删除源文件复选框
ttk.Checkbutton(
    options_frame,
    text="转换后删除源文件",
    variable=self.delete_source_var
).grid(row=0, column=0, sticky=tk.W, pady=2)

# 删除空目录复选框
ttk.Checkbutton(
    options_frame,
    text="删除空目录",
    variable=self.delete_empty_dirs_var
).grid(row=0, column=1, sticky=tk.W, pady=2, padx=10)

# 删除歌词文件复选框
ttk.Checkbutton(
    options_frame,
    text="同时删除歌词文件",
    variable=self.delete_lyrics_var
).grid(row=0, column=2, sticky=tk.W, pady=2)
```

#### 4.6 新增方法 - 删除源文件（第 201 行之后）

```python
def delete_source_file(self, input_file, delete_lyrics=False):
    """
    删除源文件和（可选的）歌词文件

    注意：
    - 只检查源文件是否存在，不验证歌词复制是否成功（简化方案）
    - copy_lyrics_file() 方法无需修改

    Args:
        input_file: 输入文件的完整路径
        delete_lyrics: 是否同时删除歌词文件

    Returns:
        int: 删除的文件数量
    """
    deleted_count = 0

    try:
        # 删除源音频文件（解密成功后文件一定存在）
        if os.path.exists(input_file):
            os.remove(input_file)
            deleted_count += 1
            self.log(f"✓ 已删除源文件: {os.path.basename(input_file)}")

        # 删除歌词文件（只检查源文件是否存在，不验证复制结果）
        if delete_lyrics:
            lyric_file = os.path.splitext(input_file)[0] + ".lrc"
            if os.path.exists(lyric_file):
                os.remove(lyric_file)
                deleted_count += 1
                self.log(f"✓ 已删除歌词文件: {os.path.basename(lyric_file)}")

    except Exception as e:
        self.log(f"删除文件失败: {e}", logging.WARNING)

    return deleted_count
```

#### 4.7 新增方法 - 删除空目录（第 235 行之后）

```python
def cleanup_empty_dirs(self, dir_path, root_dir):
    """
    递归删除空目录，直到 root_dir

    Args:
        dir_path: 要检查的目录路径
        root_dir: 根目录（停止删除的边界）

    Returns:
        int: 删除的目录数量
    """
    deleted_count = 0

    # 规范化路径
    dir_path = os.path.normpath(dir_path)
    root_dir = os.path.normpath(root_dir)

    # 如果已经到达根目录或超出范围，停止
    if dir_path == root_dir or not dir_path.startswith(root_dir):
        return deleted_count

    try:
        # 检查目录是否为空
        if os.path.exists(dir_path) and not os.listdir(dir_path):
            os.rmdir(dir_path)
            deleted_count += 1
            self.log(f"✓ 已删除空目录: {dir_path}")

            # 递归删除父目录
            parent_dir = os.path.dirname(dir_path)
            deleted_count += self.cleanup_empty_dirs(parent_dir, root_dir)

    except Exception as e:
        self.log(f"删除目录失败: {e}", logging.WARNING)

    return deleted_count
```

#### 4.8 修改 run_decryption 方法（第 335 行附近）

**原始代码（第 326-342 行）**:
```python
if "Success" in result:
    # 重命名临时文件
    os.rename(temp_file_path, output_file_path)
    success_files += 1
    self.log(f"✓ 解密成功: {output_file}")

    if output_file_path.lower().endswith('.flac'):
        self.add_flac_metadata(output_file_path)

    self.copy_lyrics_file(encrypted_file, output_file_path)
else:
    failed_files += 1
    # 清理临时文件...
```

**修改后（添加删除逻辑）**:
```python
if "Success" in result:
    # 重命名临时文件
    os.rename(temp_file_path, output_file_path)
    success_files += 1
    self.log(f"✓ 解密成功: {output_file}")

    if output_file_path.lower().endswith('.flac'):
        self.add_flac_metadata(output_file_path)

    # 复制歌词文件
    self.copy_lyrics_file(encrypted_file, output_file_path)

    # === 新增：删除源文件和空目录 ===
    if self.delete_source_var.get():
        # 删除源文件和歌词文件
        deleted_count = self.delete_source_file(
            encrypted_file,
            self.delete_lyrics_var.get()
        )
        self.deleted_files += deleted_count

        # 删除空目录
        if self.delete_empty_dirs_var.get():
            file_dir = os.path.dirname(encrypted_file)
            deleted_dirs = self.cleanup_empty_dirs(file_dir, input_dir)
            self.deleted_dirs += deleted_dirs
    # ===============================
else:
    failed_files += 1
    # 清理临时文件...
```

#### 4.9 修改 start_decryption 方法（第 157 行后，重置统计）

```python
# 在开始解密前重置删除统计
self.deleted_files = 0
self.deleted_dirs = 0
```

#### 4.10 修改完成日志显示（第 370 行附近）

```python
# 在完成日志中添加删除统计
message = f"""
转换完成！
==================
成功: {success_files}
失败: {failed_files}
已删除文件: {self.deleted_files}
已删除目录: {self.deleted_dirs}
==================
"""

self.log(message)
messagebox.showinfo("完成", message)
```

---

## 4. 测试计划

### 测试用例

| 编号 | 测试场景 | 输入配置 | 预期结果 |
|------|---------|----------|----------|
| TC01 | 正常删除源文件 | 删除源文件=启用, 删除歌词=启用 | .mflac 和 .lrc 都被删除 |
| TC02 | 仅删除源文件 | 删除源文件=启用, 删除歌词=禁用 | 只删除 .mflac，保留 .lrc |
| TC03 | 不删除源文件 | 删除源文件=禁用 | 不删除任何源文件 |
| TC04 | 删除空目录 | 删除空目录=启用 | 目录递归删除直到非空 |
| TC05 | 不删除空目录 | 删除空目录=禁用 | 空目录保留 |
| TC06 | 解密失败 | 解密失败 | 不执行任何删除操作 |
| TC07 | 统计信息 | 删除多个文件 | 统计正确显示 |
| TC08 | 深层目录嵌套 | 多层子目录 | 正确递归删除 |
| TC09 | 输入目录边界 | 只剩输入目录 | 停止删除，不删除输入目录 |
| TC10 | 文件存在检查 | 源文件不存在 | 不报错，继续执行 |

### 测试数据结构

```
G:\QQMusic\Download\VipSongsDownload\
├── Artist1\
│   ├── Album1\
│   │   ├── Song1.mflac
│   │   ├── Song1.lrc
│   │   └── Song2.mflac
│   └── Album2\
│       └── Song3.mflac
└── Artist2\
    └── Song4.mflac
```

**预期转换后**（删除所有源文件和空目录）:

```
G:\QQMusic\Download\VipSongsDownload\
└── Artist1\
    └── Album1\
        └── Song2.mflac    ← 未处理，保留
```

### 测试方法

1. **手动测试**:
   ```bash
   # 创建测试目录结构
   cd test_input
   mkdir -p Artist1/Album1 Artist1/Album2 Artist2
   # 创建测试文件...
   ```

2. **GUI 测试**:
   - 启动 GUI
   - 选择测试输入/输出目录
   - 勾选/取消勾选删除选项
   - 运行解密
   - 检查输出和源目录

3. **CLI 测试**:
   ```bash
   python main_cli.py --input test_input --output test_output
   ```

4. **验证**:
   - 检查源文件是否删除
   - 检查空目录是否删除
   - 检查统计信息是否正确
   - 检查解密文件是否正确

---

## 5. 修改清单

### config.ini

| 位置 | 操作 |
|------|------|
| [PATHS] 部分 | 更新默认路径为 VipSongsDownload |
| [OPTIONS] 部分 | 添加 3 行删除配置项 |

### main_cli.py

| 位置 | 行号 | 操作 |
|------|------|------|
| __init__ 方法 | ~36行后 | 添加 3 个配置变量 |
| __init__ 方法 | ~48行后 | 添加 2 个统计变量 |
| copy_lyrics_file 方法后 | ~285行后 | 添加 delete_source_file() 方法 |
| delete_source_file 方法后 | 新增 | 添加 cleanup_empty_dirs() 方法 |
| decrypt_file 方法 | ~362行后 | 调用删除逻辑 |
| save_stats 方法 | ~502行后 | 添加删除统计保存 |
| main() 函数 | ~574行后 | 添加配置读取 |

### gui_backup/main_gui.py

| 位置 | 行号 | 操作 |
|------|------|------|
| 导入区域 | 第12行 | 添加 import configparser |
| __init__ 方法 | 第27行前 | 添加 self.load_config() 调用 |
| load_config 方法 | 新增 | 添加配置读取方法（约45行） |
| 变量定义 | 第31行后 | 添加 3 个复选框变量 + 2 个统计变量（从配置读取默认值）|
| 设置默认路径 | 第101行 | 使用配置文件的路径 |
| 新增界面控件 | 第66行后 | 添加 3 个复选框控件 |
| start_decryption 方法 | 第157行后 | 重置删除统计 |
| copy_lyrics_file 方法后 | 第201行后 | 添加 delete_source_file() 方法 |
| delete_source_file 方法后 | 新增 | 添加 cleanup_empty_dirs() 方法 |
| run_decryption 方法 | 第335行后 | 调用删除逻辑 |
| 完成日志 | 第370行附近 | 显示删除统计 |

---

## 6. 实施步骤

### 步骤 1：备份原始文件

```bash
# 备份配置文件
copy config.ini config.ini.backup

# 备份 CLI 版本
copy main_cli.py main_cli.py.backup

# 备份 GUI 版本
copy gui_backup\main_gui.py gui_backup\main_gui.py.backup
```

### 步骤 2：修改配置文件

1. 打开 `config.ini`
2. 在 `[OPTIONS]` 部分添加：
   ```ini
   delete_source = true
   delete_empty_dirs = true
   delete_lyrics = true
   ```

### 步骤 3：修改 CLI 版本

1. 打开 `main_cli.py`
2. 按照代码实施部分逐步修改：
   - 添加统计变量
   - 添加删除方法
   - 修改解密逻辑
   - 修改配置读取
   - 修改统计保存

### 步骤 4：修改 GUI 版本

1. 打开 `gui_backup/main_gui.py`
2. 按照代码实施部分逐步修改：
   - 添加变量和控件
   - 添加删除方法
   - 修改解密逻辑
   - 修改完成日志

### 步骤 5：测试

1. 创建测试目录结构
2. 运行 CLI 版本测试
3. 运行 GUI 版本测试
4. 验证所有功能

### 步骤 6：文档更新

1. 更新 `AGENTS.md`
2. 更新 `README.md`
3. 创建实施报告

---

## 7. 注意事项

### 代码注意事项

- ⚠️ 路径必须使用 `os.path.normpath()` 规范化，避免路径格式不一致
- ⚠️ 删除前检查文件/目录是否存在
- ⚠️ 删除操作使用 try-except 包裹，避免异常中断程序
- ⚠️ 递归删除目录时必须检查边界条件
- ⚠️ 不要删除输入根目录本身
- ⚠️ 统计信息要准确累加

### 安全注意事项

- ⚠️ 默认启用删除，用户需谨慎使用
- ⚠️ 建议在测试环境先测试
- ⚠️ 重要文件建议先备份
- ⚠️ 删除操作不可逆

### 测试注意事项

- ⚠️ 测试时使用临时目录
- ⚠️ 测试边界条件（根目录、文件不存在等）
- ⚠️ 验证统计信息准确性
- ⚠️ 测试不同配置组合

---

## 8. 预期效果

### 日志输出示例

```
[2026-01-27 10:00:00] [INFO] QQ Music 批量解密工具 - CLI版本
[2026-01-27 10:00:00] [INFO] 找到 5 个加密文件
[2026-01-27 10:00:01] [INFO] 正在解密: 梁博 - 今天.mflac
[2026-01-27 10:00:30] [INFO] ✓ 解密成功: 梁博 - 今天.flac
[2026-01-27 10:00:30] [INFO] ✓ 已删除源文件: 梁博 - 今天.mflac
[2026-01-27 10:00:30] [INFO] ✓ 已删除歌词文件: 梁博 - 今天.lrc
[2026-01-27 10:00:30] [INFO] ✓ 已删除空目录: G:\QQMusic\Download\Artist\Album
[2026-01-27 10:00:30] [INFO] ✓ 已删除空目录: G:\QQMusic\Download\Artist
```

### 统计信息示例

```json
{
  "timestamp": "2026-01-27T10:00:00",
  "stats": {
    "total": 5,
    "success": 5,
    "failed": 0,
    "skipped": 0,
    "cleanup": {
      "deleted_files": 10,
      "deleted_dirs": 4
    }
  }
}
```

### GUI 完成提示示例

```
转换完成！
==================
成功: 5
失败: 0
已删除文件: 10
已删除目录: 4
==================
```

---

## 9. 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 误删重要文件 | 高 | 低 | 默认启用，但用户可关闭 |
| 删除非空目录 | 中 | 低 | 严格检查目录为空 |
| 路径处理错误 | 中 | 低 | 使用 os.path.normpath() |
| 统计信息不准确 | 低 | 低 | 仔细累加计数 |
| 递归深度过大 | 低 | 极低 | 目录深度通常有限 |

---

## 10. 后续优化建议

1. **撤销功能**: 提供撤销删除的功能（需要记录删除操作）
2. **日志增强**: 记录删除的文件完整路径
3. **预览模式**: 提供"预览删除"功能，不实际删除
4. **选择性删除**: 允许用户选择特定文件/目录保留
5. **性能优化**: 批量删除优化
6. **国际化**: 支持多语言界面

---

**文档版本**: v1.0
**创建日期**: 2026-01-27
**状态**: ✅ 方案完成，准备实施
