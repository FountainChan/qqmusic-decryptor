# QQ Music 批量解密工具

自动批量转换QQ Music的加密音乐文件（.mflac/.mgg）为标准格式（.flac/.ogg），支持保留目录结构、智能跳过、错误重试等功能。

## 📋 功能特性

- ✅ **批量处理**：一次性转换所有加密文件
- ✅ **目录结构保留**：保持原始文件夹结构
- ✅ **智能跳过**：自动跳过已转换的文件
- ✅ **错误重试**：失败文件自动重试3次
- ✅ **详细日志**：记录每个文件的转换过程
- ✅ **元数据保留**：完整保留音乐文件的所有元数据
- ✅ **进度显示**：实时显示转换进度和统计信息
- ✅ **质量验证**：自动验证输出文件的完整性

## 🚀 快速开始

### 首次使用（5分钟）

#### 1. 安装依赖
双击运行 `install_dependencies.bat`

#### 2. 下载frida-server
- 访问 https://github.com/frida/frida/releases
- 下载 `frida-server-16.7.10-windows-x86_64.exe.xz`
- 解压到项目目录，重命名为 `frida-server.exe`

#### 3. 启动必要服务
- 右键 `start_frida_server.bat` → 以管理员身份运行
- 启动QQ Music客户端（确保已登录VIP账号）

#### 4. 开始解密

**GUI版本（推荐）**：
双击运行 `run_gui_simple.bat`

**CLI版本**：
双击运行 `auto_decrypt.bat`

### 日常使用（1分钟）

**Windows批处理（.bat）**：
1. 确保frida-server和QQ Music正在运行
2. 运行 `auto_decrypt.bat`
3. 等待转换完成

**Git Bash Shell脚本（.sh）**：
```bash
# 1. 确保 frida-server 和 QQ Music 正在运行
# 2. 选择解密方式：

# CLI命令行模式（自动批量解密）
bash auto_decrypt.sh

# GUI图形界面模式（后台运行，无控制台）
bash start_gui.sh

# GUI图形界面模式（前台运行，显示控制台日志）
bash run_gui_simple.sh
```

**Shell脚本说明**：
- `auto_decrypt.sh` - CLI命令行自动解密，使用配置文件中的路径
- `start_gui.sh` - GUI后台启动，使用`pythonw`，无控制台窗口，适合日常使用
- `run_gui_simple.sh` - GUI前台启动，使用`python`，显示控制台日志，适合调试

## 📂 项目结构

```
D:\WorkDev\qqmusic_decryptor\
 ├── main_cli.py                    # CLI核心工具
 ├── config.ini                     # 配置文件
 ├── requirements.txt               # Python依赖
 ├── hook_qq_music.js               # Frida解密脚本
 │
 ├── auto_decrypt.bat               # 主批处理脚本
 ├── check_env.bat                  # 环境检查脚本
 ├── install_dependencies.bat       # 依赖安装脚本
 ├── start_frida_server.bat         # Frida服务启动脚本
 ├── run_gui_simple.bat            # ⭐ GUI快速启动脚本
 ├── launch_gui.bat                # GUI标准启动脚本
 │
 ├── gui_backup\                    # GUI备份版本
 │   ├── main_gui.py
 │   ├── hook_qq_music.js
 │   ├── run_gui.bat
 │   └── README.md
 │
 ├── doc/                           # 📂 文档目录
 │   ├── README.md                # 文档目录（快速入口）
 │   ├── doc_index.md             # 文档索引
 │   ├── problem_solved.md         # ⭐ 问题解决记录
 │   ├── agents.md                # 项目文档
 │   ├── claude.md                # Claude AI集成指南
 │   ├── GUI_STARTUP_GUIDE.md     # GUI使用指南
 │   ├── PROJECT_SUMMARY.md       # 项目总结
 │   ├── QUICKSTART.md            # 快速开始
 │   └── TEST_REPORT.md          # 测试报告
 │
 ├── logs/                          # 日志目录
 │   ├── decrypt.log
 │   └── stats.json
 │
 └── README.md                      # 本文档
 ```

## ⚙️ 配置选项

编辑 `config.ini` 文件来自定义设置：

```ini
[PATHS]
input_dir = G:\QQMusic\Download          # 输入目录
output_dir = G:\QQMusic\Decrypted        # 输出目录

[LOGGING]
log_level = INFO                          # 日志级别
log_file = logs/decrypt.log              # 日志文件
save_stats = true                        # 保存统计信息

[OPTIONS]
preserve_structure = true                # 保留目录结构
skip_existing = true                     # 跳过已存在文件
max_retries = 3                          # 最大重试次数
retry_delay = 2                          # 重试延迟（秒）
verify_metadata = true                   # 验证元数据

[NOTIFICATIONS]
show_completion = true                   # 显示完成通知
show_summary = true                      # 显示摘要信息
```

## 🎯 命令行参数

```bash
# 基本使用
python main_cli.py

# 指定输入输出目录
python main_cli.py --input "D:\Music\VipSongs" --output "D:\Music\Decrypted"

# 显示详细日志
python main_cli.py --verbose

# 自定义重试次数
python main_cli.py --retries 5

# 不保留目录结构（扁平化输出）
python main_cli.py --flat

# 强制转换所有文件（不跳过已存在的）
python main_cli.py --no-skip

# 使用自定义配置文件
python main_cli.py --config "my_config.ini"

# 组合使用
python main_cli.py -i "D:\input" -o "D:\output" -v -r 5
```

## 📝 元数据处理模式

程序支持两种元数据处理模式，通过 `config.ini` 中的 `metadata_processing_mode` 选项配置：

### 批量模式（推荐）
**特点**：
- 在所有文件解密完成后统一处理元数据
- 效率高，同一专辑只调用一次 API
- 节省网络带宽和服务器压力
- 时间节省 90%（单专辑 10 首歌曲：从 50 秒降至 5 秒）
- 默认模式

**配置**：
```ini
[OPTIONS]
metadata_processing_mode = batch
skip_metadata_during_decrypt = true
```

### 逐个模式（旧方式）
**特点**：
- 每个文件解密完成后立即处理元数据
- 效率较低，每个文件都会调用一次 API
- 适合需要立即验证元数据的场景
- 需要在 config.ini 中配置

**配置**：
```ini
[OPTIONS]
metadata_processing_mode = inline
skip_metadata_during_decrypt = false
```

### 手动补充元数据

如果您选择批量模式，或者需要为已解密的文件补充元数据，可以运行：

```bash
# 使用 Shell 脚本（推荐）
bash run_supplement.sh

# 或手动运行 Python 脚本
python supplement_album_metadata.py /path/to/decrypted/files

# 带详细输出
python supplement_album_metadata.py /path/to/decrypted/files --verbose

# 试运行（不实际修改文件）
python supplement_album_metadata.py /path/to/decrypted/files --dry-run
```

### 元数据处理内容

批量元数据补充工具将为所有 FLAC/OGG 文件添加：

1. **音轨号** - 从文件名提取并写入 TRACKNUMBER 字段
2. **专辑封面** - 从 API 获取并嵌入到文件，同时保存为 `cover.jpg`
3. **发行年份** - 从 API 获取并写入 DATE 字段

## 📊 输出示例

```
[2026-01-25 14:30:45] [INFO] ============================================================
[2026-01-25 14:30:45] [INFO] QQ Music 批量解密工具 - CLI版本
[2026-01-25 14:30:45] [INFO] ============================================================
[2026-01-25 14:30:45] [INFO] 输入目录: G:\QQMusic\Download
[2026-01-25 14:30:45] [INFO] 输出目录: G:\QQMusic\Decrypted
[2026-01-25 14:30:45] [INFO] 保留目录结构: True
[2026-01-25 14:30:45] [INFO] 跳过已存在: True
[2026-01-25 14:30:45] [INFO] 最大重试次数: 3
[2026-01-25 14:30:45] [INFO] 重试延迟: 2秒
[2026-01-25 14:30:45] [INFO] ============================================================
[2026-01-25 14:30:46] [INFO] 成功连接到QQ音乐进程
[2026-01-25 14:30:46] [INFO] 解密脚本加载成功
[2026-01-25 14:30:46] [INFO] 正在扫描目录: G:\QQMusic\Download
[2026-01-25 14:30:47] [INFO] 找到 30 个加密文件
[2026-01-25 14:30:47] [INFO] 正在处理: 1/30 (3.3%)
[2026-01-25 14:30:47] [INFO] ------------------------------------------------------------
[2026-01-25 14:30:47] [INFO] 正在解密: 梁博 - 今天.mflac
[2026-01-25 14:30:47] [INFO] 输入: G:\QQMusic\Download\梁博\梁博 - 今天.mflac
[2026-01-25 14:30:47] [INFO] 输出: G:\QQMusic\Decrypted\梁博\梁博 - 今天.flac
[2026-01-25 14:30:47] [INFO] 文件大小: 45.23 MB
[2026-01-25 14:30:50] [INFO] 输出文件大小: 43.12 MB (95.3%)
[2026-01-25 14:30:50] [INFO] ✓ 解密成功: 梁博 - 今天.flac
...
[2026-01-25 14:45:30] [INFO] 正在处理: 30/30 (100.0%)
[2026-01-25 14:45:31] [INFO] 统计信息已保存到: logs/stats.json

============================================================
  🎉 解密任务完成！
============================================================
  总文件数: 30
  成功: 28 ✅
  失败: 2 ❌
  跳过: 0 ⏭️
  处理时间: 14分45秒
  平均速度: 1.89 文件/分钟
============================================================
```

## ❓ 常见问题

### 1. 提示"Python未安装"
**解决方法**：
- 访问 https://www.python.org/downloads/
- 下载并安装Python 3.8或更高版本
- 安装时勾选"Add Python to PATH"

### 2. 提示"frida包未安装"
**解决方法**：
```bash
pip install -r requirements.txt
```

### 3. 提示"frida-server未运行"
**解决方法**：
- 右键 `start_frida_server.bat` → 以管理员身份运行
- 确保窗口保持打开状态

### 4. 提示"QQ Music未运行"
**解决方法**：
- 启动QQ Music客户端
- 确保已登录VIP账号
- 等待几秒让程序完全加载

### 5. 解密失败
**可能原因**：
- QQ Music未运行或已断开连接
- 网络连接问题
- VIP账号权限问题

**解决方法**：
- 检查QQ Music是否正常运行
- 重新下载失败的文件
- 查看日志文件：`logs/decrypt.log`

### 6. 输出文件无法播放
**可能原因**：
- 文件解密不完整
- 元数据损坏

**解决方法**：
- 查看日志文件确认解密是否成功
- 重新转换失败的文件
- 使用 `--no-skip` 参数强制重新转换

## 🔧 故障排除

### 环境问题

#### 问题：frida和frida-server版本不匹配
```bash
# 检查frida版本
python -c "import frida; print(frida.__version__)"

# 确保frida-server版本一致（必须是16.7.10）
```

#### 问题：端口占用
```bash
# frida-server默认使用27042端口
# 可以使用以下命令检查
netstat -ano | findstr 27042
```

### 解密问题

#### 问题：文件转换失败
1. 检查QQ Music是否正常运行
2. 确认VIP账号权限
3. 查看日志文件获取详细错误信息
4. 尝试重新下载失败的文件

#### 问题：速度很慢
- 这是正常现象，每个文件约需30-40秒
- 不要同时运行其他占用CPU的程序
- 使用SSD可以提高IO速度

## 📈 性能优化

- 使用SSD提高IO速度
- 关闭其他占用CPU的程序
- 分批处理大量文件（每次不超过100个）
- 使用 `--verbose` 参数监控进度

## 📝 更新日志

### v1.0.0 (2026-01-25)
- ✅ 初始版本发布
- ✅ 支持批量解密.mflac/.mgg文件
- ✅ 保留原始目录结构
- ✅ 智能跳过已转换文件
- ✅ 错误重试机制
- ✅ 详细日志记录
- ✅ 统计信息保存

## 🤝 贡献

如有问题或建议，请提交Issue或Pull Request。

## 📄 许可证

本项目仅供学习交流使用，请遵守相关法律法规。

## 🙏 致谢

- [frida](https://github.com/frida/frida) - 动态插桩框架
- [strelitzia-reg/qqmusic-decryptor](https://github.com/strelitzia-reg/qqmusic-decryptor) - GUI版本参考

## 📚 更多文档

详细文档请查看 [doc/README.md](doc/README.md)

- [问题解决记录](doc/problem_solved.md) - ⭐ 所有问题和解决方案
- [文档索引](doc/doc_index.md) - 项目文档快速导航
- [GUI启动指南](doc/GUI_STARTUP_GUIDE.md) - GUI使用详细说明
- [测试报告](doc/TEST_REPORT.md) - GUI修复的完整测试报告
