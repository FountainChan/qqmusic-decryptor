# 歌词文件复制功能 - 简化版开发文档

## 1. 需求说明

### 功能描述

在音频文件解密成功后，自动复制同名的歌词文件（.lrc）到输出目录。

**关键规则**：
- ✅ 只在转换成功后检查源目录是否有同名 .lrc 文件
- ✅ 有就直接复制，没有就忽略
- ✅ 如果歌词文件已存在就直接覆盖
- ✅ 不需要歌词复制统计变量
- ✅ 不需要添加配置项
- ✅ GUI 保持原样，不添加歌词复制信息展示
- ✅ 保持目录结构，与 .flac 文件在同一目录下

### 输入输出示例

**输入**:
```
G:\QQMusic\Download\VipSongsDownload\歌手\专辑\
├── 歌曲.mflac
├── 歌曲.lrc
└── 其他.mflac
```

**输出**:
```
G:\QQMusic\Decrypted\VipSongsDownload\歌手\专辑\
├── 歌曲.flac      ← 解密成功
├── 歌曲.lrc       ← 自动复制
└── 其他.flac      ← 解密成功
```

### 处理逻辑

```
对于每个加密文件：
    1. 解密音频文件
    2. 如果解密成功：
        a. 检查是否存在同名 .lrc 文件（在输入目录）
        b. 如果存在：
           - 计算输出目录中的歌词文件路径
           - 创建输出目录（如果需要）
           - 复制歌词文件（如果已存在则覆盖）
        c. 如果不存在：
           - 忽略，不进行任何操作
    3. 如果解密失败：
        - 不处理歌词文件
```

---

## 2. 代码分析

### GUI 版本 (gui_backup/main_gui.py)

**需要修改的位置**：

1. **第6行** - 导入模块
   ```python
   import os
   import hashlib
   import threading
   import logging
   import sys
   from datetime import datetime
   import shutil  # 新增
   ```

2. **第309行之后** - 添加辅助方法
   ```python
   def copy_lyrics_file(self, input_file, output_file):
       """
       复制同名的歌词文件到输出目录

       Args:
           input_file: 输入音频文件的完整路径
           output_file: 输出音频文件的完整路径
       """
       # 构建歌词文件路径
       input_lyric = os.path.splitext(input_file)[0] + ".lrc"
       output_lyric = os.path.splitext(output_file)[0] + ".lrc"

       # 检查歌词文件是否存在
       if not os.path.exists(input_lyric):
           return  # 不存在则忽略

       try:
           # 创建输出目录
           os.makedirs(os.path.dirname(output_lyric), exist_ok=True)

           # 复制歌词文件
           shutil.copy2(input_lyric, output_lyric)
       except Exception as e:
           pass  # 不处理错误，保持简化
   ```

3. **第286行之后** - 在解密成功后调用
   ```python
   # 原始代码（第282-286行）
   if "Success" in result:
       # 重命名临时文件
       os.rename(temp_file_path, output_file_path)
       success_files += 1
       self.log(f"✓ 解密成功: {output_file}")

       # 复制歌词文件（新增）
       self.copy_lyrics_file(encrypted_file, output_file_path)
   ```

**可用变量**：
- `encrypted_file` - 输入文件的完整路径（第246行）
- `file_name` - 输入文件名（第247行）
- `output_file_path` - 输出文件的完整路径（第260行）
- `relative_path` - 相对路径（第259行）

---

### CLI 版本 (main_cli.py)

**需要修改的位置**：

1. **第11行** - 导入模块
   ```python
   import frida
   import os
   import hashlib
   import sys
   import json
   import time
   from datetime import datetime
   from pathlib import Path
   import configparser
   import shutil  # 新增
   ```

2. **第331行之后** - 添加辅助方法
   ```python
   def copy_lyrics_file(self, input_file, output_file):
       """
       复制同名的歌词文件到输出目录

       Args:
           input_file: 输入音频文件的完整路径
           output_file: 输出音频文件的完整路径
       """
       # 构建歌词文件路径
       input_lyric = os.path.splitext(input_file)[0] + ".lrc"
       output_lyric = os.path.splitext(output_file)[0] + ".lrc"

       # 检查歌词文件是否存在
       if not os.path.exists(input_lyric):
           return  # 不存在则忽略

       try:
           # 创建输出目录
           os.makedirs(os.path.dirname(output_lyric), exist_ok=True)

           # 复制歌词文件
           shutil.copy2(input_lyric, output_lyric)
       except Exception as e:
           pass  # 不处理错误，保持简化
   ```

3. **第308行之前** - 在解密成功日志之前调用
   ```python
   # 原始代码（第283-309行）
   if "Success" in result:
       # 重命名为最终文件名
       os.rename(temp_file_path, output_file)

       # 验证输出文件
       if output_file.lower().endswith('.flac'):
           if not self.verify_flac_file(output_file):
               os.remove(output_file)
               self.log("FLAC验证失败，删除文件", "ERROR")
               raise Exception("FLAC validation failed")

       # 检查输出文件大小...（省略中间代码）

       # 复制歌词文件（新增）
       self.copy_lyrics_file(input_file, output_file)

       self.log(f"✓ 解密成功: {os.path.basename(output_file)}", "INFO")
       return "success"
   ```

**可用变量**：
- `input_file` - 输入文件的完整路径（参数传入）
- `filename` - 输入文件名（第262行）
- `output_file` - 输出文件的完整路径（第244行调用get_output_path）
- `temp_file_path` - 临时文件路径（第265行）

---

## 3. 测试计划

### 测试用例

| 编号 | 测试场景 | 输入 | 预期输出 |
|------|---------|------|----------|
| TC01 | 正常情况-歌词存在 | song.mflac + song.lrc | song.flac + song.lrc |
| TC02 | 歌词不存在 | 只有 song.mflac | 只有 song.flac |
| TC03 | 目录结构保持 | 子目录/song.mflac + song.lrc | 子目录/song.flac + song.lrc |
| TC04 | 覆盖已有歌词 | 输出已有 song.lrc | 覆盖 song.lrc |
| TC05 | 解密失败 | song.mflac + song.lrc 但解密失败 | 不生成任何文件 |

### 测试方法

1. 创建测试目录结构
2. 运行 GUI 或 CLI 版本
3. 检查输出目录
4. 验证歌词文件是否正确复制

---

## 4. 修改清单

### GUI 版本

| 位置 | 行号 | 操作 |
|------|------|------|
| 导入模块 | ~6行 | 添加 `import shutil` |
| 添加方法 | 第309行后 | 添加 `copy_lyrics_file()` 方法 |
| 调用位置 | 第286行后 | 添加 `self.copy_lyrics_file(encrypted_file, output_file_path)` |

### CLI 版本

| 位置 | 行号 | 操作 |
|------|------|------|
| 导入模块 | ~11行 | 添加 `import shutil` |
| 添加方法 | 第331行后 | 添加 `copy_lyrics_file()` 方法 |
| 调用位置 | 第308行前 | 添加 `self.copy_lyrics_file(input_file, output_file)` |

---

## 5. 完整代码片段

### GUI 版本完整修改

```python
# 1. 导入模块（第6行附近）
import os
import hashlib
import threading
import logging
import sys
from datetime import datetime
import shutil  # 新增

# 2. 添加辅助方法（第309行之后）
def copy_lyrics_file(self, input_file, output_file):
    """
    复制同名的歌词文件到输出目录

    Args:
        input_file: 输入音频文件的完整路径
        output_file: 输出音频文件的完整路径
    """
    # 构建歌词文件路径
    input_lyric = os.path.splitext(input_file)[0] + ".lrc"
    output_lyric = os.path.splitext(output_file)[0] + ".lrc"

    # 检查歌词文件是否存在
    if not os.path.exists(input_lyric):
        return  # 不存在则忽略

    try:
        # 创建输出目录
        os.makedirs(os.path.dirname(output_lyric), exist_ok=True)

        # 复制歌词文件
        shutil.copy2(input_lyric, output_lyric)
    except Exception as e:
        pass  # 不处理错误，保持简化

# 3. 调用位置（第286行之后）
if "Success" in result:
    # 重命名临时文件
    os.rename(temp_file_path, output_file_path)
    success_files += 1
    self.log(f"✓ 解密成功: {output_file}")

    # 复制歌词文件（新增）
    self.copy_lyrics_file(encrypted_file, output_file_path)
```

### CLI 版本完整修改

```python
# 1. 导入模块（第11行附近）
import frida
import os
import hashlib
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import configparser
import shutil  # 新增

# 2. 添加辅助方法（第331行之后）
def copy_lyrics_file(self, input_file, output_file):
    """
    复制同名的歌词文件到输出目录

    Args:
        input_file: 输入音频文件的完整路径
        output_file: 输出音频文件的完整路径
    """
    # 构建歌词文件路径
    input_lyric = os.path.splitext(input_file)[0] + ".lrc"
    output_lyric = os.path.splitext(output_file)[0] + ".lrc"

    # 检查歌词文件是否存在
    if not os.path.exists(input_lyric):
        return  # 不存在则忽略

    try:
        # 创建输出目录
        os.makedirs(os.path.dirname(output_lyric), exist_ok=True)

        # 复制歌词文件
        shutil.copy2(input_lyric, output_lyric)
    except Exception as e:
        pass  # 不处理错误，保持简化

# 3. 调用位置（第308行之前）
if "Success" in result:
    # 重命名为最终文件名
    os.rename(temp_file_path, output_file)

    # 验证输出文件
    if output_file.lower().endswith('.flac'):
        if not self.verify_flac_file(output_file):
            os.remove(output_file)
            self.log("FLAC验证失败，删除文件", "ERROR")
            raise Exception("FLAC validation failed")

    # 检查输出文件大小...（省略中间代码）

    # 复制歌词文件（新增）
    self.copy_lyrics_file(input_file, output_file)

    self.log(f"✓ 解密成功: {os.path.basename(output_file)}", "INFO")
    return "success"
```

---

## 6. 实施步骤

### 步骤1：备份原始文件
```bash
# 备份 GUI 版本
copy gui_backup\main_gui.py gui_backup\main_gui.py.backup

# 备份 CLI 版本
copy main_cli.py main_cli.py.backup
```

### 步骤2：修改 GUI 版本
1. 使用文本编辑器打开 `gui_backup/main_gui.py`
2. 在第6行附近添加 `import shutil`
3. 在第309行后添加 `copy_lyrics_file()` 方法
4. 在第286行后添加 `self.copy_lyrics_file(encrypted_file, output_file_path)`

### 步骤3：修改 CLI 版本
1. 使用文本编辑器打开 `main_cli.py`
2. 在第11行附近添加 `import shutil`
3. 在第331行后添加 `copy_lyrics_file()` 方法
4. 在第308行前添加 `self.copy_lyrics_file(input_file, output_file)`

### 步骤4：测试
1. 创建测试目录结构
2. 运行 `run_gui_simple.bat`
3. 检查输出目录
4. 验证歌词文件是否正确复制

---

## 7. 注意事项

### 代码注意事项
- ⚠️ 导入语句必须放在文件开头
- ⚠️ 辅助方法应放在类的其他方法附近
- ⚠️ 调用位置必须在解密成功判断之后
- ⚠️ 方法名必须与文档一致

### 测试注意事项
- ⚠️ 确保输入目录中有 .lrc 文件
- ⚠️ 检查输出目录的目录结构
- ⚠️ 验证歌词文件内容是否正确
- ⚠️ 测试覆盖已存在文件的情况

---

## 8. 总结

### 修改范围
- ✅ **2个文件**：gui_backup/main_gui.py、main_cli.py
- ✅ **6处修改**：每个文件3处（导入 + 方法 + 调用）
- ✅ **极简实现**：不需要配置、不需要统计

### 实施难度
- ⭐ **难度**：低 - 代码逻辑简单
- ⏱️ **预计时间**：15-30分钟

### 验证方法
- 📝 手动测试
- 🔍 检查输出目录
- 🎧 播放测试（可选）

---

**文档版本**: v3.0（最终简化版）
**创建日期**: 2026-01-26
**状态**: ✅ 计划完成，准备实施
