# QQ音乐解密技能 - 部署完成

## 技能已成功创建

QQ 音乐解密工具已成功封装为 AI 助手技能！

## 触发关键词

当你说以下任一关键词时，AI 将自动启动解密工具：

- **转换音乐**
- **解密音乐**
- **解码音乐**
- **转换flac**
- **转换ogg**
- **解密mflac**
- **解密mgg**

## 使用示例

```
你: 转换音乐
AI: [检查环境] → [启动 GUI] → [等待操作]

你: 帮我解密音乐
AI: [验证前置条件] → [打开解密工具] → [提示配置]

你: 解码音乐
AI: [启动 CLI 模式] → [批量处理]
```

## 技能文件结构

```
D:\WorkDev\qqmusic_decryptor\
├── .skills/                          # 技能定义目录
│   ├── qqmusic_decryptor.json         # JSON 格式技能定义
│   └── qqmusic_decryptor.md          # Markdown 格式技能文档
├── skill_launcher.py                 # 技能启动器（Python）
├── SKILL_README.md                  # 技能使用说明
└── ... (其他项目文件)
```

## 技能功能

### 自动化流程

1. **环境检查**
   - Python 版本（3.8+）
   - frida 包安装（16.7.10）
   - mutagen 包安装（≥1.47.0）
   - frida-server 运行状态
   - QQ Music 运行状态

2. **启动工具**
   - GUI 模式：打开图形界面
   - CLI 模式：运行命令行版本

3. **解密功能**
   - 批量转换 .mflac/.mgg 文件
   - 保留原始目录结构
   - 自动复制 .lrc 歌词文件
   - 自动添加音轨号元数据

### 智能特性

- ✅ 前置条件自动检查
- ✅ 错误提示和解决方案
- ✅ 双模式支持（GUI/CLI）
- ✅ 日志记录和统计
- ✅ 错误重试机制

## 前置条件

使用前需要确保：

### 必需条件

1. **Python 环境**
   ```
   python --version
   # 应显示 Python 3.8 或更高版本
   ```

2. **依赖包安装**
   ```bash
   pip install -r requirements.txt
   # 包含: frida==16.7.10, mutagen>=1.47.0
   ```

3. **frida-server 运行**
   ```
   # 以管理员身份运行
   start_frida_server.bat
   # 保持窗口打开
   ```

4. **QQ Music 运行**
   - 启动 QQ Music 客户端
   - 登录 VIP 账号

### 快速检查

运行环境检查脚本：
```bash
python skill_launcher.py
```

## 手动运行

如果不想使用技能触发，也可以手动运行：

### GUI 模式
```batch
run_gui_simple.bat
```

### CLI 模式
```batch
auto_decrypt.bat
```

### 技能启动器
```bash
python skill_launcher.py
```

## 配置说明

### 默认路径

- **输入目录**：`G:\QQMusic\Download`
- **输出目录**：`G:\QQMusic\Decrypted\VipSongsDownload`

### 修改配置

编辑 `config.ini` 文件：
```ini
[PATHS]
input_dir = 你的输入目录
output_dir = 你的输出目录
```

## 功能特性

### 核心功能

- ✅ 批量解密 .mflac/.mgg 文件
- ✅ 转换为标准 .flac/.ogg 格式
- ✅ 保留原始目录结构
- ✅ 智能跳过已转换文件
- ✅ 错误重试机制（最多3次）

### 增强功能

- ✅ 自动复制 .lrc 歌词文件
- ✅ 自动添加音轨号元数据
- ✅ 从文件名提取音轨号
- ✅ 详细日志记录
- ✅ 统计信息保存

### 支持格式

| 输入格式 | 输出格式 | 音质 |
|----------|----------|------|
| .mflac | .flac | 无损 |
| .mgg | .ogg | 有损 |

## 故障排除

### 问题：技能启动失败

**检查项**：
1. Python 是否安装（3.8+）
2. 依赖包是否安装
3. frida-server 是否运行
4. QQ Music 是否运行

**解决方法**：
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 frida-server（管理员）
start_frida_server.bat

# 3. 启动 QQ Music
```

### 问题：找不到模块

**错误信息**：
```
ModuleNotFoundError: No module named 'mutagen'
```

**解决方法**：
```bash
pip install mutagen
```

### 问题：frida-server 未运行

**错误信息**：
```
frida-server 未运行
```

**解决方法**：
- 右键 `start_frida_server.bat`
- 选择"以管理员身份运行"
- 保持窗口打开状态

### 问题：解密失败

**检查项**：
1. QQ Music 是否正常登录 VIP
2. 网络连接是否正常
3. 文件是否完整

**日志位置**：
```
logs/decrypt.log
```

## 性能指标

| 指标 | 预期值 |
|------|--------|
| 转换成功率 | ≥95% |
| 平均速度 | 1.5-2个文件/分钟 |
| 单文件时间 | 30-40秒 |
| 内存占用 | <300MB |
| CPU 占用 | 10-30% |

## 文档索引

- **完整文档**：`docs/README.md`
- **快速开始**：`docs/QUICKSTART.md`
- **项目总结**：`docs/PROJECT_SUMMARY.md`
- **音轨号功能**：`docs/FLAC_METADATA_RESEARCH.md`
- **问题解决**：`docs/problem_solved.md`
- **技能说明**：`SKILL_README.md`

## 使用流程

### 完整流程

```
1. 触发技能
   ↓
2. 检查前置条件
   ↓
3. 启动解密工具（GUI 或 CLI）
   ↓
4. 配置输入/输出目录（仅 GUI）
   ↓
5. 开始解密
   ↓
6. 等待完成
   ↓
7. 查看结果和日志
```

### 示例对话

```
你: 转换音乐

AI: 正在检查前置条件...
    [OK] Python 版本: 3.11.8
    [OK] frida 已安装: 16.7.10
    [OK] mutagen 已安装
    [OK] frida-server 正在运行
    [OK] QQ Music 正在运行

    请选择启动方式:
    1. GUI 模式（推荐，图形界面）
    2. CLI 模式（命令行）

你: 1

AI: [启动 GUI] → 等待配置...

你: [在 GUI 中设置路径并点击开始]

AI: [执行解密] → [显示进度] → 完成！
```

## 注意事项

### 使用注意

1. **frida-server**：整个解密过程必须保持运行
2. **QQ Music VIP**：需要有效的 VIP 账号
3. **磁盘空间**：确保有足够空间存储解密文件
4. **文件权限**：确保有读写权限

### 安全说明

- 本工具仅供个人学习使用
- 请遵守相关法律法规
- 不要用于商业用途

## 技能版本信息

- **技能名称**：qqmusic_decryptor
- **技能版本**：1.0.0
- **创建日期**：2026-01-26
- **项目路径**：D:\WorkDev\qqmusic_decryptor

## 获取帮助

如果遇到问题：

1. **查看文档**：`docs/` 目录
2. **查看日志**：`logs/decrypt.log`
3. **检查环境**：`python skill_launcher.py`
4. **运行诊断**：`check_env.bat`

---

**技能部署完成！现在可以直接说"转换音乐"来启动解密工具了。**
