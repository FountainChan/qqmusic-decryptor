# QQ Music 解密工具 - 问题解决记录

> 本文档记录了项目中遇到的所有问题及其解决方案

**最后更新**: 2026-01-26
**项目路径**: `D:\WorkDev\qqmusic_decryptor`

---

## 目录

1. [问题1: 输出目录配置错误](#问题1-输出目录配置错误)
2. [问题2: 目录结构保留失败](#问题2-目录结构保留失败)
3. [问题3: 批处理文件编码问题](#问题3-批处理文件编码问题)
4. [问题4: 临时文件名冲突](#问题4-临时文件名冲突)
5. [问题5: GUI启动脚本一闪而过](#问题5-gui启动脚本一闪而过)

---

## 问题1: 输出目录配置错误

### 问题描述

- **现象**: GUI的默认输出目录为 `D:\DecryptedMusic`
- **期望**: 输出目录应该是 `G:\QQMusic\Decrypted\VipSongsDownload`

### 根因分析

**文件**: `gui_backup/main_gui.py`

**位置**: 第99行

```python
# 修复前（错误）
self.output_path.set("D:\\DecryptedMusic")
```

硬编码了错误的默认路径，导致每次启动GUI都需要手动修改输出目录。

### 解决方案

**修复内容**:

```python
# 修复后（正确）
self.output_path.set("G:\\QQMusic\\Decrypted\\VipSongsDownload")
```

### 验证方法

运行测试脚本：
```bash
python test_gui_config.py
```

### 相关文件

- `gui_backup/main_gui.py:99`
- `test_gui_config.py`
- `check_current_paths.py`

---

## 问题2: 目录结构保留失败

### 问题描述

- **现象**: 解密后的文件被扁平化输出到输出目录，丢失了原始的目录结构
- **期望**: 保留原始的 `歌手\专辑\歌曲` 目录结构

**示例**:
- 输入: `G:\QQMusic\Download\VipSongsDownload\歌手\专辑\歌曲.mflac`
- 期望输出: `G:\QQMusic\Decrypted\VipSongsDownload\歌手\专辑\歌曲.flac`
- 实际输出: `G:\QQMusic\Decrypted\VipSongsDownload\歌曲.flac` (错误)

### 根因分析

**文件**: `gui_backup/main_gui.py`

**位置**: 第245-256行

**问题代码**:
```python
# 修复前（错误）
file_name = os.path.basename(encrypted_file)  # 只提取文件名
# ...
output_file_path = os.path.join(output_dir, output_file)  # 扁平化输出
```

只使用了 `os.path.basename()` 提取文件名，丢失了相对路径信息。

### 解决方案

**修复内容**:

```python
# 修复后（正确）
# 获取相对路径以保留目录结构
relative_path = os.path.relpath(encrypted_file, input_dir)
file_name = os.path.basename(encrypted_file)

# 构建输出文件名
file_ext = os.path.splitext(file_name)[-1].lower()
if file_ext == ".mflac":
    output_ext = ".flac"
else:  # .mgg
    output_ext = ".ogg"

# 替换扩展名并保留目录结构
relative_path = os.path.splitext(relative_path)[0] + output_ext
output_file_path = os.path.join(output_dir, relative_path)

# 创建输出目录（包含子目录）
output_dir_with_path = os.path.dirname(output_file_path)
os.makedirs(output_dir_with_path, exist_ok=True)
```

**关键改进**:
1. 使用 `os.path.relpath()` 获取相对路径
2. 保留目录结构信息
3. 使用 `os.makedirs()` 自动创建子目录

### 验证方法

运行测试脚本：
```bash
python test_gui_functions.py
```

**测试用例**:
```python
# 测试1: 单层目录
输入: G:\QQMusic\Download\VipSongsDownload\Song.mflac
输出: G:\QQMusic\Decrypted\VipSongsDownload\Song.flac

# 测试2: 多层目录
输入: G:\QQMusic\Download\VipSongsDownload\Artist\Album\Song.mflac
输出: G:\QQMusic\Decrypted\VipSongsDownload\Artist\Album\Song.flac

# 测试3: .mgg格式
输入: G:\QQMusic\Download\VipSongsDownload\Artist\Album\Song.mgg
输出: G:\QQMusic\Decrypted\VipSongsDownload\Artist\Album\Song.ogg
```

### 相关文件

- `gui_backup/main_gui.py:245-264`
- `test_gui_functions.py`
- `TEST_REPORT.md`

---

## 问题3: 批处理文件编码问题

### 问题描述

- **现象**: 双击 `quick_start_gui.bat` 运行时，出现中文乱码错误
- **错误信息**:
  ```
  '鏋淕UI绐楀彛娌℃湁鎵撳紜锛岃妫€鏌ワ細' 不是内部或外部命令，也不是可运行的程序
  'frida鍖呮槸鍚﹀畨瑁咃紙鐗堟湰16.7.10锛?echo' 不是内部或外部命令，也不是可运行的程序
  ```

### 根因分析

**原因**:
- Windows批处理文件默认使用 GBK/ANSI 编码
- 文件中的中文字符在命令行中被错误解析
- 导致整行命令被当作一个奇怪的"命令"

**问题文件**: `quick_start_gui.bat`

### 解决方案

#### 方案1: 创建纯英文批处理文件（推荐）

创建了 `run_gui_simple.bat`，只包含英文：

```batch
@echo off
cd /d "%~dp0"

pythonw gui_backup\main_gui.py
```

#### 方案2: 使用 CMD 手动运行（最可靠）

```batch
# 按 Win + R，输入 cmd
cd D:\WorkDev\qqmusic_decryptor
pythonw gui_backup\main_gui.py
```

#### 方案3: 设置编码（可选）

在批处理文件开头添加：
```batch
chcp 65001 >nul
```

但这在某些情况下可能不起作用。

### 最佳实践

**推荐使用**: `run_gui_simple.bat`

**优点**:
- 无编码问题
- 简单直接
- 不会一闪而过

### 相关文件

- `run_gui_simple.bat`
- `start_gui_english.bat`
- `GUI_STARTUP_GUIDE.md`

---

## 问题4: 临时文件名冲突

### 问题描述

- **现象**: 当输入目录中存在同名文件（不同子目录）时，临时文件名会冲突
- **场景**:
  ```
  G:\QQMusic\Download\VipSongsDownload\Artist1\Song.mflac
  G:\QQMusic\Download\VipSongsDownload\Artist2\Song.mflac
  ```
  两个文件会生成相同的临时文件名，导致冲突。

### 根因分析

**文件**: `gui_backup/main_gui.py`

**位置**: 第274行

**问题代码**:
```python
# 修复前（错误）
temp_file_name = hashlib.md5(file_name.encode()).hexdigest()  # 只用文件名
temp_file_path = os.path.join(output_dir, temp_file_name)
```

只使用了文件名（`Song.mflac`）进行MD5哈希，导致同名文件生成相同的哈希值。

### 解决方案

**修复内容**:

```python
# 修复后（正确）
temp_file_name = hashlib.md5(encrypted_file.encode()).hexdigest() + output_ext
temp_file_path = os.path.join(output_dir, temp_file_name)
```

**关键改进**: 使用完整文件路径（`G:\...\Artist1\Song.mflac`）进行哈希，确保每个文件有唯一的临时文件名。

### 验证方法

运行测试：
```bash
python test_gui_functions.py
```

**测试用例**:
```python
file1 = r"G:\QQMusic\Download\VipSongsDownload\Song.mflac"
file2 = r"G:\QQMusic\Download\VipSongsDownload\Other\Song.mflac"

temp1 = hashlib.md5(file1.encode()).hexdigest() + ".flac"
temp2 = hashlib.md5(file2.encode()).hexdigest() + ".flac"

# 验证: temp1 != temp2
```

### 相关文件

- `gui_backup/main_gui.py:274`
- `test_gui_functions.py`

---

## 问题5: GUI启动脚本一闪而过

### 问题描述

- **现象**: 双击 `quick_start_gui.bat` 窗口一闪而过，看不到输出信息
- **原因**: 使用 `timeout` 命令后自动退出

### 根因分析

**问题代码**:
```batch
timeout /t 3 >nul
```

3秒后窗口自动关闭，如果用户没注意到就消失了。

### 解决方案

**修复内容**:

使用 `pause` 等待用户按键：

```batch
echo 按任意键关闭此窗口...
pause >nul
```

**优点**:
- 窗口会一直打开，直到用户按键
- 可以查看所有输出信息
- 可以看到任何错误信息

### 最佳实践

**推荐**: 使用 `run_gui_simple.bat`（不需要等待）

**理由**:
- GUI会在后台启动
- 批处理文件执行完就退出
- 不需要用户干预

### 相关文件

- `run_gui_simple.bat`
- `quick_start_gui.bat` (已修复)

---

## 快速参考

### 启动GUI的推荐方法

#### 方法1: 双击批处理文件（推荐）
```
双击: run_gui_simple.bat
```

#### 方法2: CMD命令行（最可靠）
```batch
cd D:\WorkDev\qqmusic_decryptor
pythonw gui_backup\main_gui.py
```

#### 方法3: 右键以管理员运行
```
右键: run_gui_simple.bat → 以管理员身份运行
```

### 默认配置

| 配置项 | 值 |
|--------|-----|
| 输入目录 | `G:\QQMusic\Download\VipSongsDownload` |
| 输出目录 | `G:\QQMusic\Decrypted\VipSongsDownload` |
| 目录结构保留 | 完整保留 |
| 文件格式转换 | `.mflac` → `.flac`, `.mgg` → `.ogg` |

### 测试脚本

```bash
# 配置验证
python test_gui_config.py

# 功能测试
python test_gui_functions.py

# 环境诊断
python diagnose_gui.py
```

### 检查当前配置

```bash
python check_current_paths.py
```

### 备份信息

原始文件备份位置:
```
D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py.bak
```

恢复方法（如需要）:
```batch
copy "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py.bak" ^
     "D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
```

---

## 环境要求

### 必需的进程

1. **frida-server**
   - 启动命令: `start_frida_server.bat`（管理员权限）
   - 状态检查: `tasklist /FI "IMAGENAME eq frida-server.exe"`

2. **QQ Music**
   - 需要已登录VIP账号
   - 状态检查: `tasklist /FI "IMAGENAME eq QQMusic.exe"`

### Python环境

- **Python版本**: 3.8+
- **Frida版本**: 16.7.10（必须与frida-server一致）
- **tkinter**: Python标准库，应自动包含

### 目录权限

- 读取权限: `G:\QQMusic\Download\VipSongsDownload`
- 写入权限: `G:\QQMusic\Decrypted\VipSongsDownload`

---

## 故障排除

### GUI 窗口没有打开

1. 检查frida-server是否运行
2. 检查QQ Music是否运行
3. 检查Python是否正确安装
4. 运行诊断脚本: `python diagnose_gui.py`

### 转换失败

1. 确保QQ Music已登录VIP账号
2. 检查输入目录中的文件是否有效
3. 查看GUI日志窗口中的错误信息
4. 尝试重新启动frida-server和QQ Music

### 目录结构没有保留

1. 确认使用的是修复后的版本
2. 检查 `gui_backup/main_gui.py` 第245-264行
3. 运行测试: `python test_gui_functions.py`

### 批处理文件乱码

1. 使用 `run_gui_simple.bat`（纯英文）
2. 或在CMD中手动运行命令
3. 检查系统编码设置

---

## 相关文档

- `TEST_REPORT.md` - 完整测试报告
- `GUI_STARTUP_GUIDE.md` - GUI启动指南
- `agents.md` - 项目综合文档
- `claude.md` - AI助手使用指南
- `README.md` - 项目说明

---

## 更新日志

### v1.1 (2026-01-26)

**修复**:
- ✅ 输出目录配置错误
- ✅ 目录结构保留失败
- ✅ 临时文件名冲突问题
- ✅ 批处理文件编码问题
- ✅ GUI启动脚本一闪而过

**新增**:
- ✅ 测试脚本（`test_gui_config.py`, `test_gui_functions.py`）
- ✅ 诊断脚本（`diagnose_gui.py`）
- ✅ 配置检查脚本（`check_current_paths.py`）
- ✅ 简化的启动脚本（`run_gui_simple.bat`）
- ✅ 问题解决文档（本文件）

### v1.0 (2026-01-25)

**初始版本**:
- ✅ 基本的解密功能
- ✅ GUI界面
- ✅ CLI版本

---

## 贡献者

- Claude AI Assistant
- User feedback and testing

---

## 许可证

本项目仅供学习交流使用，请遵守相关法律法规。

---

**文档版本**: 1.1
**最后更新**: 2026-01-26
**状态**: ✅ 所有问题已解决
