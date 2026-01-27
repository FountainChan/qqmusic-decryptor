# FLAC 音轨号元数据添加研究报告

## 一、Python 库调研与推荐

### 1.1 主要 Python 库对比

| 库名称 | 功能 | 优点 | 缺点 | 推荐指数 |
|--------|------|------|------|----------|
| **Mutagen** | 支持FLAC、MP3、OGG等20+种音频格式的元数据读写 | - API简单易用<br>- 支持Unicode<br>- 无外部依赖<br>- 活跃维护<br>- 被Picard、Beets等知名项目使用 | - 相对较重的库 | ⭐⭐⭐⭐⭐ |
| pyflac | 专门用于FLAC文件处理 | - 轻量级<br>- 专注FLAC格式 | - 功能有限<br>- 不及Mutagen全面 | ⭐⭐⭐ |
| audioread | 音频文件读取库 | - 简单 | - 只能读取，不能写入元数据 | ⭐ |
| tinytag | 轻量级元数据读取 | - 非常轻量 | - 只能读取，不能写入 | ⭐ |

### 1.2 推荐库：Mutagen

**推荐理由：**
1. **行业标准**：被 MusicBrainz Picard、Beets、Puddletag 等知名音乐标签软件使用
2. **完整功能**：支持读写所有 FLAC 元数据字段
3. **简单API**：统一的 API 设计，不同格式用法一致
4. **零依赖**：不依赖任何第三方库，只使用 Python 标准库
5. **成熟稳定**：项目历史悠久，文档完善，社区活跃

## 二、FLAC 音轨号元数据字段详解

### 2.1 标准字段名称

FLAC 使用 Vorbis Comment 格式存储元数据，音轨号相关的标准字段为：

| 字段名称 | 含义 | 是否必需 | 格式示例 |
|----------|------|----------|----------|
| **TRACKNUMBER** | 当前音轨号 | 否（但推荐） | "1", "12", "01" |
| **TRACKTOTAL** | 专辑总音轨数 | 否 | "10", "12" |

### 2.2 数据格式规范

- **字段类型**：字符串（String）
- **编码格式**：UTF-8
- **数值格式**：虽然存储为字符串，但应该是纯数字字符
- **不区分大小写**：Vorbis Comment 规范要求字段名称不区分大小写，但通常使用大写

### 2.3 相关标准字段（可选）

| 字段名称 | 含义 |
|----------|------|
| TITLE | 歌曲标题 |
| ARTIST | 艺术家 |
| ALBUM | 专辑名称 |
| DATE | 发行日期（ISO 8601格式：YYYY-MM-DD） |
| GENRE | 音乐类型 |

## 三、实现方案设计

### 3.1 文件名解析逻辑

```python
import re
import os

def extract_track_number_from_filename(filename):
    """
    从文件名中提取音轨号

    支持的文件名格式：
    - "01 歌曲名.flac"
    - "1-歌曲名.flac"
    - "12. 另一首歌.flac"
    - "歌曲名.flac" (返回 None)

    Args:
        filename (str): 文件名（不含路径）

    Returns:
        int or None: 提取到的音轨号，如果未找到则返回 None
    """
    # 移除扩展名
    basename = os.path.splitext(filename)[0]

    # 尝试匹配开头的数字
    # 模式1: 数字+空格 (如 "01 歌曲名")
    match = re.match(r'^(\d+)\s', basename)
    if match:
        return int(match.group(1))

    # 模式2: 数字+分隔符 (如 "1-歌曲名", "12.歌曲名")
    match = re.match(r'^(\d+)[\-\.\s]', basename)
    if match:
        return int(match.group(1))

    # 模式3: 纯数字前缀 (如 "12歌曲名")
    match = re.match(r'^(\d+)', basename)
    if match:
        # 确保数字后面还有内容（不是整个文件名都是数字）
        if len(match.group(1)) < len(basename):
            return int(match.group(1))

    # 未找到音轨号
    return None
```

### 3.2 写入音轨号到 FLAC 文件

```python
from mutagen.flac import FLAC
import os
import logging

def add_track_number_to_flac(flac_file_path, track_number, total_tracks=None):
    """
    为 FLAC 文件添加音轨号元数据

    Args:
        flac_file_path (str): FLAC 文件路径
        track_number (int): 音轨号
        total_tracks (int, optional): 专辑总音轨数

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(flac_file_path):
            logging.error(f"文件不存在: {flac_file_path}")
            return False

        # 检查是否是FLAC文件
        if not flac_file_path.lower().endswith('.flac'):
            logging.error(f"不是FLAC文件: {flac_file_path}")
            return False

        # 加载FLAC文件
        audio = FLAC(flac_file_path)

        # 设置音轨号（转换为字符串）
        audio["TRACKNUMBER"] = str(track_number)

        # 如果提供了总音轨数，也设置
        if total_tracks is not None:
            audio["TRACKTOTAL"] = str(total_tracks)

        # 保存元数据
        audio.save()

        logging.info(f"成功添加音轨号: {track_number} 到 {os.path.basename(flac_file_path)}")
        return True

    except Exception as e:
        logging.error(f"添加音轨号失败 {os.path.basename(flac_file_path)}: {e}")
        return False
```

### 3.3 完整处理函数（集成文件名解析）

```python
def process_flac_file_metadata(flac_file_path, total_tracks=None, verbose=False):
    """
    处理单个 FLAC 文件的元数据（从文件名提取并添加音轨号）

    Args:
        flac_file_path (str): FLAC 文件路径
        total_tracks (int, optional): 专辑总音轨数
        verbose (bool): 是否输出详细日志

    Returns:
        dict: 处理结果 {'success': bool, 'track_number': int or None, 'message': str}
    """
    result = {
        'success': False,
        'track_number': None,
        'message': ''
    }

    try:
        # 提取音轨号
        filename = os.path.basename(flac_file_path)
        track_number = extract_track_number_from_filename(filename)

        if track_number is None:
            result['message'] = f"未从文件名提取到音轨号: {filename}"
            if verbose:
                logging.info(result['message'])
            return result

        # 添加音轨号
        success = add_track_number_to_flac(flac_file_path, track_number, total_tracks)

        if success:
            result['success'] = True
            result['track_number'] = track_number
            result['message'] = f"成功添加音轨号 {track_number}"
            if verbose:
                logging.info(result['message'])
        else:
            result['message'] = f"添加音轨号失败: {filename}"

        return result

    except Exception as e:
        result['message'] = f"处理异常 {filename}: {e}"
        logging.error(result['message'])
        return result
```

### 3.4 批量处理函数

```python
def process_directory_flac_metadata(directory_path, total_tracks=None, verbose=False):
    """
    批量处理目录中所有 FLAC 文件的元数据

    Args:
        directory_path (str): 目录路径
        total_tracks (int, optional): 专辑总音轨数
        verbose (bool): 是否输出详细日志

    Returns:
        dict: 统计信息 {'total': int, 'success': int, 'failed': int, 'skipped': int}
    """
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    try:
        # 遍历目录
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.flac'):
                    stats['total'] += 1
                    flac_file_path = os.path.join(root, file)

                    result = process_flac_file_metadata(
                        flac_file_path,
                        total_tracks,
                        verbose
                    )

                    if result['success']:
                        stats['success'] += 1
                    elif result['track_number'] is None:
                        stats['skipped'] += 1
                    else:
                        stats['failed'] += 1

        return stats

    except Exception as e:
        logging.error(f"批量处理异常: {e}")
        return stats
```

### 3.5 错误处理方案

```python
class FLACMetadataError(Exception):
    """FLAC 元数据处理异常"""
    pass

def safe_add_track_number(flac_file_path, max_retries=2):
    """
    安全地添加音轨号（带重试机制）

    Args:
        flac_file_path (str): FLAC 文件路径
        max_retries (int): 最大重试次数

    Returns:
        bool: 成功返回 True
    """
    for attempt in range(max_retries + 1):
        try:
            filename = os.path.basename(flac_file_path)
            track_number = extract_track_number_from_filename(filename)

            if track_number is None:
                logging.debug(f"跳过（无音轨号）: {filename}")
                return False

            if add_track_number_to_flac(flac_file_path, track_number):
                return True

            elif attempt < max_retries:
                time.sleep(0.5)  # 短暂等待后重试
                continue
            else:
                return False

        except Exception as e:
            logging.error(f"尝试 {attempt + 1}/{max_retries + 1} 失败: {e}")
            if attempt < max_retries:
                time.sleep(0.5)
            else:
                return False

    return False
```

## 四、集成到现有代码

### 4.1 CLI 版本集成（main_cli.py）

**集成位置：** 在 `decrypt_file` 方法中，解密成功后调用元数据添加函数

```python
# 在 QQMusicDecryptorCLI 类中添加新方法

def add_flac_metadata(self, flac_file_path):
    """
    为 FLAC 文件添加元数据（从文件名提取音轨号）

    Args:
        flac_file_path (str): FLAC 文件路径
    """
    try:
        filename = os.path.basename(flac_file_path)
        track_number = extract_track_number_from_filename(filename)

        if track_number is not None:
            success = add_track_number_to_flac(flac_file_path, track_number)
            if success:
                self.log(f"✓ 已添加音轨号 {track_number}", "INFO")
            else:
                self.log(f"✗ 添加音轨号失败", "WARNING")
        else:
            self.log(f"未找到音轨号，跳过元数据添加", "DEBUG")

    except Exception as e:
        self.log(f"添加元数据异常: {e}", "WARNING")

# 修改 decrypt_file 方法（在成功解密后添加）
def decrypt_file(self, input_file, retry_count=0):
    # ... 现有代码 ...

    if "Success" in result:
        # 重命名为最终文件名
        os.rename(temp_file_path, output_file)

        # ... 现有的验证代码 ...

        # === 新增：添加元数据 ===
        if output_file.lower().endswith('.flac'):
            self.add_flac_metadata(output_file)
        # =======================

        self.copy_lyrics_file(input_file, output_file)
        self.log(f"✓ 解密成功: {os.path.basename(output_file)}", "INFO")
        return "success"

    # ... 其余现有代码 ...
```

### 4.2 GUI 版本集成（gui_backup/main_gui.py）

**集成位置：** 在 `run_decryption` 方法中，解密成功后调用元数据添加函数

```python
# 在 QQMusicDecryptorGUI 类中添加新方法

def add_flac_metadata(self, flac_file_path):
    """
    为 FLAC 文件添加元数据（从文件名提取音轨号）

    Args:
        flac_file_path (str): FLAC 文件路径
    """
    try:
        filename = os.path.basename(flac_file_path)
        track_number = extract_track_number_from_filename(filename)

        if track_number is not None:
            success = add_track_number_to_flac(flac_file_path, track_number)
            if success:
                self.log(f"✓ 已添加音轨号 {track_number}")
            else:
                self.log(f"✗ 添加音轨号失败", logging.WARNING)

    except Exception as e:
        self.log(f"添加元数据异常: {e}", logging.WARNING)

# 修改 run_decryption 方法（在成功解密后添加）
def run_decryption(self):
    # ... 现有代码 ...

    try:
        # 调用解密函数
        self.log(f"开始解密: {file_name}")
        result = self.script.exports_sync.decrypt(encrypted_file, temp_file_path)

        if "Success" in result:
            # 重命名临时文件
            os.rename(temp_file_path, output_file_path)
            success_files += 1
            self.log(f"✓ 解密成功: {output_file}")

            # === 新增：添加FLAC元数据 ===
            if output_file_path.lower().endswith('.flac'):
                self.add_flac_metadata(output_file_path)
            # ==========================

            self.copy_lyrics_file(encrypted_file, output_file_path)
        else:
            # ... 失败处理代码 ...

    # ... 其余现有代码 ...
```

### 4.3 影响范围评估

| 影响项 | 说明 | 影响 |
|--------|------|------|
| **依赖增加** | 需要添加 mutagen 库 | 新增 1 个依赖 |
| **代码修改量** | CLI 和 GUI 各需修改 1 处 + 添加新函数 | 约 50-80 行代码 |
| **性能影响** | 元数据写入操作（约 10-50ms/文件） | 可忽略 |
| **向后兼容** | 不影响现有功能 | 完全兼容 |
| **错误处理** | 元数据添加失败不影响解密成功状态 | 隔离处理 |

## 五、依赖管理与安装

### 5.1 安装命令

```bash
# 基本安装
pip install mutagen

# 或使用 requirements.txt
echo "mutagen>=1.47.0" >> requirements.txt
pip install -r requirements.txt
```

### 5.2 更新 requirements.txt

在项目根目录的 `requirements.txt` 文件中添加：

```txt
frida==16.7.10
mutagen>=1.47.0
```

### 5.3 版本选择建议

- **最低版本**：`>=1.47.0`（2021年发布，包含稳定的FLAC支持）
- **推荐版本**：`mutagen==1.47.0` 或更新版本
- **最新版本**：`mutagen`（不指定版本号，使用最新稳定版）

### 5.4 对现有依赖的影响

| 依赖项 | 版本 | 冲突风险 | 说明 |
|--------|------|----------|------|
| frida | 16.7.10 | 无冲突 | Mutagen 不依赖任何外部库 |
| Python | 3.x | 无冲突 | Mutagen 支持 Python 3.10+ |

## 六、完整代码示例

### 6.1 独立元数据处理模块（metadata_utils.py）

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FLAC 元数据处理工具模块
用于为 FLAC 文件添加音轨号等元数据
"""

import re
import os
import logging
from mutagen.flac import FLAC, FLACNoHeaderError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_track_number_from_filename(filename):
    """
    从文件名中提取音轨号

    支持的文件名格式：
    - "01 歌曲名.flac"
    - "1-歌曲名.flac"
    - "12. 另一首歌.flac"
    - "歌曲名.flac" (返回 None)

    Args:
        filename (str): 文件名（不含路径）

    Returns:
        int or None: 提取到的音轨号，如果未找到则返回 None
    """
    # 移除扩展名
    basename = os.path.splitext(filename)[0]

    # 尝试匹配开头的数字
    # 模式1: 数字+空格 (如 "01 歌曲名")
    match = re.match(r'^(\d+)\s', basename)
    if match:
        return int(match.group(1))

    # 模式2: 数字+分隔符 (如 "1-歌曲名", "12.歌曲名")
    match = re.match(r'^(\d+)[\-\.\s]', basename)
    if match:
        return int(match.group(1))

    # 模式3: 纯数字前缀 (如 "12歌曲名")
    match = re.match(r'^(\d+)', basename)
    if match:
        # 确保数字后面还有内容（不是整个文件名都是数字）
        if len(match.group(1)) < len(basename):
            return int(match.group(1))

    # 未找到音轨号
    return None


def add_track_number_to_flac(flac_file_path, track_number, total_tracks=None):
    """
    为 FLAC 文件添加音轨号元数据

    Args:
        flac_file_path (str): FLAC 文件路径
        track_number (int): 音轨号
        total_tracks (int, optional): 专辑总音轨数

    Returns:
        bool: 成功返回 True，失败返回 False
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(flac_file_path):
            logger.error(f"文件不存在: {flac_file_path}")
            return False

        # 检查是否是FLAC文件
        if not flac_file_path.lower().endswith('.flac'):
            logger.error(f"不是FLAC文件: {flac_file_path}")
            return False

        # 加载FLAC文件
        audio = FLAC(flac_file_path)

        # 设置音轨号（转换为字符串）
        audio["TRACKNUMBER"] = str(track_number)

        # 如果提供了总音轨数，也设置
        if total_tracks is not None:
            audio["TRACKTOTAL"] = str(total_tracks)

        # 保存元数据
        audio.save()

        logger.info(f"成功添加音轨号: {track_number} 到 {os.path.basename(flac_file_path)}")
        return True

    except FLACNoHeaderError:
        logger.error(f"不是有效的FLAC文件: {flac_file_path}")
        return False
    except Exception as e:
        logger.error(f"添加音轨号失败 {os.path.basename(flac_file_path)}: {e}")
        return False


def process_flac_file_metadata(flac_file_path, total_tracks=None, verbose=False):
    """
    处理单个 FLAC 文件的元数据（从文件名提取并添加音轨号）

    Args:
        flac_file_path (str): FLAC 文件路径
        total_tracks (int, optional): 专辑总音轨数
        verbose (bool): 是否输出详细日志

    Returns:
        dict: 处理结果 {'success': bool, 'track_number': int or None, 'message': str}
    """
    result = {
        'success': False,
        'track_number': None,
        'message': ''
    }

    try:
        # 提取音轨号
        filename = os.path.basename(flac_file_path)
        track_number = extract_track_number_from_filename(filename)

        if track_number is None:
            result['message'] = f"未从文件名提取到音轨号: {filename}"
            if verbose:
                logger.info(result['message'])
            return result

        # 添加音轨号
        success = add_track_number_to_flac(flac_file_path, track_number, total_tracks)

        if success:
            result['success'] = True
            result['track_number'] = track_number
            result['message'] = f"成功添加音轨号 {track_number}"
            if verbose:
                logger.info(result['message'])
        else:
            result['message'] = f"添加音轨号失败: {filename}"

        return result

    except Exception as e:
        result['message'] = f"处理异常 {filename}: {e}"
        logger.error(result['message'])
        return result


def process_directory_flac_metadata(directory_path, total_tracks=None, verbose=False):
    """
    批量处理目录中所有 FLAC 文件的元数据

    Args:
        directory_path (str): 目录路径
        total_tracks (int, optional): 专辑总音轨数
        verbose (bool): 是否输出详细日志

    Returns:
        dict: 统计信息 {'total': int, 'success': int, 'failed': int, 'skipped': int}
    """
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    try:
        # 遍历目录
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.lower().endswith('.flac'):
                    stats['total'] += 1
                    flac_file_path = os.path.join(root, file)

                    result = process_flac_file_metadata(
                        flac_file_path,
                        total_tracks,
                        verbose
                    )

                    if result['success']:
                        stats['success'] += 1
                    elif result['track_number'] is None:
                        stats['skipped'] += 1
                    else:
                        stats['failed'] += 1

        return stats

    except Exception as e:
        logger.error(f"批量处理异常: {e}")
        return stats


# 命令行使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='FLAC 元数据处理工具')
    parser.add_argument('path', help='FLAC 文件或目录路径')
    parser.add_argument('--total', type=int, help='专辑总音轨数')
    parser.add_argument('--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    if os.path.isfile(args.path):
        # 处理单个文件
        result = process_flac_file_metadata(args.path, args.total, args.verbose)
        print(f"处理结果: {result}")
    elif os.path.isdir(args.path):
        # 处理目录
        stats = process_directory_flac_metadata(args.path, args.total, args.verbose)
        print(f"统计: 总计 {stats['total']}, 成功 {stats['success']}, "
              f"失败 {stats['failed']}, 跳过 {stats['skipped']}")
    else:
        print(f"错误: 路径不存在: {args.path}")
```

### 6.2 使用示例

```python
# 示例1：处理单个文件
from metadata_utils import process_flac_file_metadata

result = process_flac_file_metadata(
    "D:/Music/01 Song Title.flac",
    total_tracks=12,
    verbose=True
)
print(result)
# 输出: {'success': True, 'track_number': 1, 'message': '成功添加音轨号 1'}

# 示例2：批量处理目录
from metadata_utils import process_directory_flac_metadata

stats = process_directory_flac_metadata(
    "D:/Music/Album/",
    total_tracks=12,
    verbose=True
)
print(stats)
# 输出: {'total': 12, 'success': 12, 'failed': 0, 'skipped': 0}

# 示例3：只提取音轨号（不写入）
from metadata_utils import extract_track_number_from_filename

track = extract_track_number_from_filename("01 Song Title.flac")
print(track)  # 输出: 1
```

## 七、总结与建议

### 7.1 推荐方案总结

| 项目 | 推荐方案 |
|------|----------|
| **Python库** | Mutagen（>=1.47.0） |
| **音轨号字段** | TRACKNUMBER（必需）、TRACKTOTAL（可选） |
| **数据格式** | UTF-8 编码的字符串 |
| **集成位置** | 解密成功后立即添加 |
| **错误处理** | 失败不影响解密结果，仅记录日志 |

### 7.2 实施步骤

1. **安装依赖**
   ```bash
   pip install mutagen
   ```

2. **创建工具模块**
   - 将上述 `metadata_utils.py` 保存到项目目录

3. **修改CLI版本**
   - 在 `main_cli.py` 中导入 `metadata_utils`
   - 修改 `decrypt_file` 方法，添加元数据处理调用

4. **修改GUI版本**
   - 在 `gui_backup/main_gui.py` 中导入 `metadata_utils`
   - 修改 `run_decryption` 方法，添加元数据处理调用

5. **更新文档**
   - 更新 `requirements.txt`
   - 更新使用说明

### 7.3 注意事项

1. **性能影响**：每个文件额外耗时约 10-50ms，可忽略
2. **错误隔离**：元数据添加失败不应影响解密结果
3. **兼容性**：保持向后兼容，不破坏现有功能
4. **日志记录**：建议记录元数据操作结果以便调试
5. **测试建议**：先用少量文件测试，确认效果后再批量使用

### 7.4 扩展功能建议

未来可考虑添加的元数据字段：

```python
# 可以扩展添加更多元数据字段
def add_metadata_from_filename(flac_file_path):
    """
    从文件名提取更多信息（可选）

    支持: "专辑名 - 01 歌曲名.flac" 等格式
    """
    # 实现更复杂的文件名解析
    # 提取：专辑名、艺术家、歌曲标题等
    pass
```

---

**文档创建时间**：2026-01-26
**研究版本**：v1.0
