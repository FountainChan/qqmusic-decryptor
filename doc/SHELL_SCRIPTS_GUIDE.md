# Shell 脚本使用指南

## 概述

本项目提供了一套 Shell 脚本（.sh 文件），用于在 Git Bash 环境下运行解密工具。相比 Windows 原生的 .bat 文件，Shell 脚本提供了更好的兼容性和功能。

## 脚本列表

### 1. start_gui.sh
**用途**：启动 GUI 图形界面解密工具

**使用方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
bash start_gui.sh
```

**功能**：
- 检查 Python 环境
- 检查 GUI 文件是否存在
- 使用 pythonw 启动 GUI（后台运行）
- 显示启动状态和日志位置

### 2. start_frida_server.sh
**用途**：启动 frida-server 服务

**使用方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
bash start_frida_server.sh
```

**注意**：
- 需要管理员权限
- 窗口必须保持打开状态
- 完成解密后可以关闭

### 3. auto_decrypt.sh
**用途**：批量解密所有文件（CLI 命令行模式）

**使用方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
bash auto_decrypt.sh

# 或带参数运行
bash auto_decrypt.sh --input "/d/Download" --output "/d/Output"
```

**功能**：
- 自动读取配置文件
- 批量处理所有加密文件
- 显示解密进度
- 生成统计信息

### 4. check_env.sh
**用途**：检查解密工具所需的环境和依赖

**使用方法**：
```bash
cd /d/WorkDev/qqmusic_decryptor
bash check_env.sh
```

**检查项目**：
1. Python 版本（3.8+）
2. frida 包安装（16.7.10）
3. mutagen 包安装
4. frida-server 运行状态
5. QQ Music 运行状态
6. 目录结构完整性
7. 配置文件存在性

## 快速开始

### 方式一：使用 Shell 脚本（推荐）

```bash
# 1. 检查环境
cd /d/WorkDev/qqmusic_decryptor
bash check_env.sh

# 2. 启动 frida-server（需要管理员）
bash start_frida_server.sh

# 3. 启动 GUI（新窗口）
bash start_gui.sh
```

### 方式二：使用 GUI 模式

```bash
# 直接启动 GUI
cd /d/WorkDev/qqmusic_decryptor
bash start_gui.sh
```

### 方式三：使用 CLI 模式

```bash
# 批量解密
cd /d/WorkDev/qqmusic_decryptor
bash auto_decrypt.sh
```

## 路径格式

在 Git Bash 中使用 **Unix 风格路径**（正斜杠 `/`）：

| Windows 路径 | Git Bash 路径 |
|---------------|----------------|
| `D:\WorkDev\qqmusic_decryptor` | `/d/WorkDev/qqmusic_decryptor` |
| `G:\QQMusic\Download` | `/g/QQMusic/Download` |
| `G:\QQMusic\Decrypted` | `/g/QQMusic/Decrypted` |

### 路径转换规则

- **盘符转换**：`D:\` → `/d/`，`G:\` → `/g/`
- **分隔符转换**：`\` → `/`
- **空格处理**：用引号包裹：`"/d/My Documents"`

## 常见问题

### 1. 权限被拒绝

**问题**：`bash: ./frida-server.exe: Permission denied`

**解决**：
```bash
# 设置执行权限
chmod +x frida-server.exe

# 或者使用 bash 启动
bash frida-server.exe
```

### 2. frida-server 检查失败

**问题**：`[FAIL] frida 命令未找到`

**解决**：
```bash
# 安装 frida-tools
pip install frida-tools

# 或者直接启动 frida-server
bash start_frida_server.sh
```

### 3. 路径错误

**问题**：`No such file or directory`

**解决**：
- 使用绝对路径：`/d/WorkDev/qqmusic_decryptor`
- 转换反斜杠为正斜杠
- 用引号包裹包含空格的路径

### 4. 脚本无法执行

**问题**：`Permission denied: ./start_gui.sh`

**解决**：
```bash
# 添加执行权限
chmod +x start_gui.sh

# 或使用 bash 运行
bash start_gui.sh
```

## 脚本对比

| 功能 | .bat 脚本 | .sh 脚本 | 推荐度 |
|------|------------|------------|--------|
| 启动 GUI | `run_gui_simple.bat` | `start_gui.sh` | ⭐⭐⭐⭐⭐ |
| 启动 frida-server | `start_frida_server.bat` | `start_frida_server.sh` | ⭐⭐⭐⭐ |
| 批量解密 | `auto_decrypt.bat` | `auto_decrypt.sh` | ⭐⭐⭐⭐⭐ |
| 环境检查 | `check_env.bat` | `check_env.sh` | ⭐⭐⭐⭐⭐ |

## 优势

### Shell 脚本的优势

1. **跨平台兼容**
   - 可以在 Linux、macOS、Windows（Git Bash）上运行
   - 统一的脚本语言和语法

2. **强大的功能**
   - 更丰富的命令和工具
   - 更好的管道和重定向支持
   - 更灵活的脚本编程

3. **路径处理**
   - 自动处理路径转换
   - 支持通配符和模式匹配
   - 更好的路径解析

4. **错误处理**
   - 更完善的错误捕获
   - 清晰的错误信息
   - 更好的调试支持

## 使用建议

### 首次使用

```bash
# 1. 检查环境
bash check_env.sh

# 2. 安装依赖（如有问题）
pip install -r requirements.txt

# 3. 启动 frida-server（管理员）
bash start_frida_server.sh

# 4. 启动 GUI
bash start_gui.sh
```

### 日常使用

```bash
# 方式一：GUI 模式
bash start_gui.sh

# 方式二：CLI 模式
bash auto_decrypt.sh
```

### 故障排除

```bash
# 检查环境
bash check_env.sh

# 查看日志
cat logs/decrypt.log

# 查看统计
cat logs/stats.json
```

## 开发建议

### 创建新的 Shell 脚本

```bash
#!/bin/bash
# 脚本说明

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查依赖
if ! command -v python &> /dev/null; then
    echo "[错误] Python 未安装"
    exit 1
fi

# 执行操作
echo "开始执行..."
# 你的代码

echo "完成！"
```

### 脚本最佳实践

1. **使用 shebang**：`#!/bin/bash`
2. **获取脚本目录**：使用 `$(dirname "${BASH_SOURCE[0]}")`
3. **错误检查**：检查命令返回值
4. **用户友好**：提供清晰的错误信息
5. **日志记录**：记录重要操作和错误

## 总结

Shell 脚本提供了更强大、更灵活的运行方式，推荐在 Git Bash 环境下使用。

**推荐流程**：
1. 使用 `check_env.sh` 检查环境
2. 使用 `start_frida_server.sh` 启动服务
3. 使用 `start_gui.sh` 或 `auto_decrypt.sh` 开始解密

**优势**：
- ✅ 跨平台兼容
- ✅ 更强大的功能
- ✅ 更好的路径处理
- ✅ 更完善的错误处理

---

**文档创建时间**：2026-01-29
