# QQ Music 解密工具 - Agents 文档

## 项目概述

本项目是一个基于Frida动态插桩技术的QQ音乐批量解密工具，用于将QQ音乐的加密音乐文件（`.mflac`/`.mgg`）转换为标准格式（`.flac`/`.ogg`）。

### 核心信息

- **项目名称**：QQ Music 批量解密工具
- **项目路径**：D:\WorkDev\qqmusic_decryptor
- **Python版本要求**：3.8+
- **Frida版本**：16.7.10（必须与frida-server版本一致）
- **主要功能**：批量解密、保留目录结构、智能跳过、错误重试、详细日志

---

## AI 助手规则

### 回答语言规则

- **使用中文回答**：所有 AI 助手在与用户交互时必须使用中文进行回答
- **文档语言**：项目相关文档和说明应使用中文编写
- **代码注释**：代码注释应使用中文，便于理解和维护

### 命令行工具使用规则

- **优先使用 Git Bash**：当需要执行命令行操作时，首先尝试使用 Git Bash 运行
- **避免 PowerShell 和 CMD**：尽量少用 PowerShell、cmd.exe 等 Windows 原生工具
- **支持 Shell 脚本**：可以使用 Git Bash 执行 .sh 脚本文件
- **路径格式**：在 Git Bash 中使用 Unix 风格路径（正斜杠 `/`），如 `/d/WorkDev/qqmusic_decryptor`
- **命令兼容性**：确保命令在 Git Bash（基于 MSYS2/MinGW）环境下可正常运行

---

## 开发经验与最佳实践

### 1. 命令行工具使用规则（新增）

**规则**：优先使用 Git Bash 执行命令行操作

**原因**：
- Git Bash 提供更好的 Unix 兼容性
- 支持更强大的 Shell 脚本（.sh）
- 避免Windows CMD/PowerShell 的路径和编码问题
- 更适合跨平台开发

**最佳实践**：
- **优先使用 Git Bash**：执行命令行操作时首先尝试 Git Bash
- **避免 Windows 原生工具**：尽量少用 PowerShell、cmd.exe
- **支持 Shell 脚本**：可以使用 .sh 脚本替代 .bat 文件
- **路径格式**：在 Git Bash 中使用 Unix 风格路径（正斜杠 `/`）
- **脚本执行**：使用 `bash script.sh` 执行 Shell 脚本

**示例**：
```bash
# 使用 Git Bash 运行命令
cd /d/WorkDev/qqmusic_decryptor
bash start_gui.sh

# 使用 .sh 脚本替代 .bat
bash check_env.sh
bash auto_decrypt.sh

# Unix 风格路径
python main_cli.py --input "/d/Download" --output "/d/Output"
```

**项目中的 Shell 脚本**：
- `start_gui.sh` - 启动 GUI 解密工具
- `start_frida_server.sh` - 启动 frida-server
- `auto_decrypt.sh` - 自动批量解密
- `check_env.sh` - 环境检查脚本

---

### 2. 批处理文件编码和编写规范

**规则**：批处理文件必须使用纯ASCII编码和CRLF换行符，避免中文字符

**原因**：
- Windows批处理文件在不同系统和终端下可能出现编码问题，导致乱码或执行失败
- Windows批处理器只识别CRLF换行符（`\r\n`），使用LF换行符（`\n`）会导致解析错误和字符截断

**最佳实践**：
- 所有批处理文件只使用ASCII字符
- 避免使用中文注释或提示信息
- 如需中文输出，使用ECHO输出中文（确保终端支持UTF-8）
- 使用CHCP 65001设置代码页以支持中文显示
- **路径使用正斜杠（/）而非反斜杠（\）**，避免路径转义问题
- **必须使用CRLF换行符（`\r\n`）**，避免字符截断错误
- 使用 `%~dp0` 获取脚本所在目录，使用相对路径
- 使用支持CRLF的编辑器（Notepad++, VS Code等）

**示例**：
```batch
@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting GUI...
python gui_backup/main_gui.py
pause
```

**错误示例**：
```batch
python gui_backup\main_gui.py  # 可能被转义为 gui_backupmain_gui.py

# 使用LF换行符会导致：
# 'ython' 不是内部或外部命令（'python' 变成 'ython'）
# 'ho' 不是内部或外部命令（'echo' 变成 'ho'）
```

**正确示例**：
```batch
python gui_backup/main_gui.py  # 使用正斜杠，跨平台兼容
```

**检测和修复命令**：
```bash
# 检测换行符类型
file filename.bat

# 修复LF换行符为CRLF
sed 's/$/\r/' input.bat > output.bat

# 或使用dos2unix工具
unix2dos filename.bat
```

---

### 2. 路径配置和目录处理

**规则**：路径配置必须使用实际路径，避免硬编码不存在的路径

**原因**：错误的默认路径会导致程序无法找到输入输出目录，影响功能

**最佳实践**：
- 配置文件中的路径必须与实际环境一致
- 使用绝对路径，避免相对路径带来的不确定性
- 提供配置验证脚本，在启动前检查路径有效性
- 在程序中添加路径存在性检查，如不存在则创建或提示用户

**示例**：
```python
def validate_paths(self):
    if not os.path.exists(self.input_dir):
        raise ValueError(f"输入目录不存在: {self.input_dir}")
    if not os.path.exists(self.output_dir):
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info(f"创建输出目录: {self.output_dir}")
```

---

### 3. 目录结构保留

**规则**：需要保留目录结构时，必须使用相对路径而非仅提取文件名

**原因**：只提取文件名会导致所有输出文件扁平化，丢失原始目录结构

**最佳实践**：
- 使用 `os.path.relpath()` 计算相对路径
- 保留输入目录到文件的所有中间目录
- 在输出前使用 `os.makedirs()` 创建必要的子目录
- 配合 `exist_ok=True` 参数避免目录已存在的错误

**示例**：
```python
relative_path = os.path.relpath(encrypted_file, input_dir)
relative_path = os.path.splitext(relative_path)[0] + output_ext
output_file_path = os.path.join(output_dir, relative_path)
output_dir_with_path = os.path.dirname(output_file_path)
os.makedirs(output_dir_with_path, exist_ok=True)
```

---

### 4. 临时文件命名和冲突避免

**规则**：生成临时文件名时必须使用完整路径，避免同名文件冲突

**原因**：不同目录下可能有同名文件，只用文件名生成MD5会导致临时文件名冲突

**最佳实践**：
- 使用文件的完整路径（包含目录）生成唯一标识
- 使用MD5或SHA-256等哈希算法生成临时文件名
- 考虑添加时间戳或进程ID进一步增强唯一性
- 临时文件应使用专门的临时目录，避免与正常文件混淆

**示例**：
```python
temp_file_name = hashlib.md5(encrypted_file.encode()).hexdigest()
temp_file_path = os.path.join(temp_dir, temp_file_name)

# 或者使用更长的唯一标识
temp_file_name = hashlib.sha256(encrypted_file.encode()).hexdigest()
```

---

### 5. GUI启动脚本编写规范

**规则**：GUI启动脚本必须包含错误处理和暂停机制

**原因**：脚本一闪而过时无法看到错误信息，难以诊断问题

**最佳实践**：
- 在脚本末尾添加 `pause` 命令，等待用户输入后再关闭
- 使用 `@echo off` 隐藏命令，但保留关键输出信息
- 添加错误处理，使用 `%ERRORLEVEL%` 检查执行状态
- 提供清晰的错误提示和解决方案
- **重要**：不要使用 `pause >nul`（会隐藏 pause 提示，但不会等待输入）
- **重要**：在关键步骤后添加调试信息，跟踪执行流程
- **重要**：确保所有错误路径都有对应的错误提示

**示例**：
```batch
@echo off
chcp 65001 >nul

REM 显示执行信息
echo 开始处理...

REM 执行 Python 脚本
python script.py

REM 检查执行结果
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 处理失败！错误代码: %ERRORLEVEL%
    echo 请检查错误日志
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESS] 处理完成
    echo.
    pause
)
```

---

### 5.1. 补充脚本启动规范（专辑元数据补充工具）

**规则**：专辑元数据补充脚本必须避免一闪而过

**原因**：`run_supplement.bat` 脚本在运行时一闪而过，用户看不到任何输出或错误信息

**最佳实践**：
- **不要使用 `pause >nul`**：这会隐藏 pause 提示，但不会等待用户按键
  - 错误：`pause >nul` 会让脚本立即退出
  - 正确：`pause` 或 `pause >con`

- **添加详细的执行日志**：在每个关键步骤后添加调试信息
  - `echo 执行命令: python script.py`
  - `echo Python 执行完成，错误代码: %errorlevel%`
  - 这样即使出错，也能看到脚本在哪里停下的

- **确保所有错误路径都有错误提示**：
  - Python 未找到
  - 目录不存在
  - 路径是文件
  - Python 执行失败

- **确保成功路径也有确认提示**：
  - 显示 "处理完成！"
  - 显示已添加的内容（封面、年份）
  - 显示统计信息

**示例**：
```batch
@echo off
chcp 65001 >nul
setlocal

set SCRIPT_DIR=%~dp0
set DEFAULT_INPUT_DIR=G:\QQMusic\Decrypted

REM 显示欢迎信息
echo ============================================================
echo   专辑元数据补充工具
echo ============================================================

REM 检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   错误：未找到 Python
    echo   请确保 Python 已安装并添加到 PATH 环境变量中
    echo.
    pause
    exit /b 1
)

REM 检查目录
if not exist "%DEFAULT_INPUT_DIR%" (
    echo.
    echo   错误：默认目录不存在
    echo.
    pause
    exit /b 1
)

echo.
echo 开始处理...
echo.
echo 执行命令: python "%SCRIPT_DIR%supplement_album_metadata.py" "%DEFAULT_INPUT_DIR%"
echo.

python "%SCRIPT_DIR%supplement_album_metadata.py" "%DEFAULT_INPUT_DIR%"

echo.
echo Python 执行完成，错误代码: %errorlevel%
echo.

if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo   处理失败，错误代码: %errorlevel%
    echo ============================================================
    echo.
    echo 请检查上面的错误信息
    echo.
) else (
    echo.
    echo ============================================================
    echo   处理完成！
    echo ============================================================
    echo.
    echo 已为 FLAC 文件添加：
    echo   - 专辑封面（嵌入文件）
    echo   - 封面文件（保存为 cover.jpg）
    echo   - 发行年份（写入 DATE 字段）
    echo.
)

echo.
echo 等待用户确认...
echo.
pause
```

**错误示例（一闪而过）**：
```batch
REM 错误示例：使用 pause >nul
echo 开始处理...
echo.
python script.py
echo.
pause >nul  # ❌ 这会让脚本立即退出，用户看不到任何输出！
```

**正确示例（等待输入）**：
```batch
REM 正确示例：使用 pause
echo 开始处理...
echo.
python script.py
echo.
pause  # ✅ 这会等待用户按键后才退出
```

**调试信息示例**：
```batch
echo 步骤 1：检查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo   结果: Python 未找到
    pause
    exit /b 1
)

echo 步骤 2：执行 Python 脚本
python script.py

echo 步骤 3：检查执行结果
if %errorlevel% neq 0 (
    echo   结果: 失败（错误代码: %errorlevel%）
    pause
    exit /b 1
)

echo 步骤 4：处理完成
pause
```

**关键检查清单**：
- [ ] 脚本是否等待用户输入？（使用 `pause` 而不是 `pause >nul`）
- [ ] 是否显示欢迎信息？
- [ ] 是否显示执行进度？
- [ ] 是否显示错误代码？
- [ ] 所有错误路径都有错误提示？
- [ ] 是否提供了解决方案？
- [ ] 是否显示成功完成信息？

---

### 6. 测试和验证流程

**规则**：GUI启动脚本必须包含错误处理和暂停机制

**原因**：脚本一闪而过时无法看到错误信息，难以诊断问题

**最佳实践**：
- 在脚本末尾添加 `pause` 命令，等待用户输入后再关闭
- 使用 `@echo off` 隐藏命令，但保留关键输出信息
- 添加错误处理，使用 `%ERRORLEVEL%` 检查执行状态
- 提供清晰的错误提示和解决方案

**示例**：
```batch
@echo off
chcp 65001 >nul
echo Starting QQ Music Decryption Tool GUI...
echo.

cd /d "%~dp0"
python gui_backup\main_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] GUI启动失败！错误代码: %ERRORLEVEL%
    echo 请检查Python环境和依赖安装
)

echo.
echo 按任意键退出...
pause >nul
```

---

### 6. 测试和验证流程

**规则**：每次修改后必须创建对应的测试脚本并进行验证

**原因**：缺少测试会导致问题难以发现，影响项目稳定性

**最佳实践**：
- 为每个修复创建独立的测试脚本
- 测试脚本应验证修复的具体功能
- 使用断言（assert）验证关键行为
- 测试通过后删除或移动临时测试文件
- 在文档中记录测试结果

**示例测试脚本**：
```python
def test_output_path_config():
    gui = QQMusicDecryptorGUI()
    expected = "G:\\QQMusic\\Decrypted\\VipSongsDownload"
    actual = gui.output_path.get()
    assert actual == expected, f"输出路径错误: {actual} != {expected}"
    print("✓ 输出路径配置正确")

def test_directory_structure():
    test_input = "G:\\QQMusic\\Download\\Artist\\Song.mflac"
    test_output_dir = "G:\\QQMusic\\Decrypted"
    expected_subdir = "G:\\QQMusic\\Decrypted\\Artist"
    # 验证相对路径计算和目录创建
    ...
```

---

### 7. 配置文件管理

**规则**：配置文件应包含合理的默认值，但允许用户自定义

**原因**：默认值应适合大多数用户，但必须支持自定义以满足不同需求

**最佳实践**：
- 在config.ini中提供清晰注释说明每个配置项的用途
- 使用合理的默认值（如项目相关的实际路径）
- 提供配置验证功能，检查配置的有效性
- 支持通过命令行参数覆盖配置文件

---

### 8. 错误处理和日志记录

**规则**：所有关键操作必须有错误处理和日志记录

**原因**：完善的错误处理和日志记录有助于问题诊断和维护

**最佳实践**：
- 使用try-except捕获可能出现的异常
- 记录详细的错误信息，包括时间、位置、原因
- 对于可恢复的错误，提供重试机制
- 对于严重错误，提供清晰的错误提示和解决建议

**示例**：
```python
try:
    result = decrypt_file(encrypted_file, output_file)
    logging.info(f"解密成功: {output_file}")
except Exception as e:
    logging.error(f"解密失败: {encrypted_file}, 错误: {str(e)}")
    if retry_count < max_retries:
        logging.info(f"重试中... ({retry_count + 1}/{max_retries})")
    else:
        logging.error(f"达到最大重试次数，跳过文件")
```

---

### 9. 文件组织和管理

**规则**：临时文件和测试文件应与核心文件分离

**原因**：清晰的文件组织有助于项目维护和理解

**最佳实践**：
- 使用专门的目录存放临时文件（如 `drops/`）
- 使用 `doc/` 目录存放文档
- 定期清理不再需要的临时文件
- 为重要文件创建备份（如 `.bak` 后缀）

---

### 10. 文档更新同步

**规则**：每次修复或功能更新后必须同步更新相关文档

**原因**：过时的文档会导致使用困惑和维护困难

**最佳实践**：
- 修复问题后，更新问题解决记录（problem_solved.md）
- 添加新功能后，更新使用说明和README
- 创建测试报告，记录测试结果
- 定期整理文档，删除过时内容

---

## 核心组件

### 1. 主程序

#### main_cli.py（555行）
- **用途**：命令行界面的核心解密工具
- **关键类**：QQMusicDecryptorCLI
- **主要方法**：
  - connect_to_qqmusic()：连接到QQ Music进程
  - load_decrypt_script()：加载Frida解密脚本
  - decrypt_file()：解密单个文件
  - decrypt_all()：批量解密所有文件
  - verify_flac_file()：验证FLAC文件完整性
  - save_stats()：保存统计信息到JSON

#### gui_backup/main_gui.py
- **用途**：图形界面版本
- **框架**：tkinter
- **功能**：提供用户友好的GUI界面进行文件解密

### 2. Frida Hook脚本

#### hook_qq_music.js（120行）
- **目标DLL**：QQMusicCommon.dll
- **关键函数**：
  - EncAndDesMediaFile：QQ Music的加密/解密媒体文件类
  - 方法：Constructor, Open, GetSize, Read, Destructor
- **工作原理**：
  1. 分配对象内存
  2. 调用构造函数
  3. 打开加密文件
  4. 读取文件大小
  5. 分块读取解密后的数据（每次64KB）
  6. 写入到临时文件
  7. 重命名为目标文件
  8. 调用析构函数清理资源

### 3. 配置文件

#### config.ini
```ini
[PATHS]
input_dir = G:\QQMusic\Download      # 输入目录（加密文件）
output_dir = G:\QQMusic\Decrypted    # 输出目录（解密后文件）

[LOGGING]
log_level = INFO                      # 日志级别
log_file = logs/decrypt.log          # 日志文件路径
save_stats = true                    # 保存统计信息

[OPTIONS]
preserve_structure = true            # 保留目录结构
skip_existing = true                 # 跳过已存在的文件
max_retries = 3                      # 最大重试次数
retry_delay = 2                      # 重试延迟（秒）
verify_metadata = true               # 验证元数据

[NOTIFICATIONS]
show_completion = true               # 显示完成通知
show_summary = true                  # 显示摘要信息
```

### 4. 自动化脚本

#### auto_decrypt.bat
- **用途**：主批处理脚本，一键启动解密任务
- **功能**：
  - 调用环境检查脚本
  - 运行CLI解密工具
  - 显示执行结果

#### start_frida_server.bat
- **用途**：启动frida-server（需要管理员权限）
- **重要提示**：必须保持窗口打开状态

#### install_dependencies.bat
- **用途**：安装Python依赖
- **依赖**：frida==16.7.10

#### check_env.bat
- **用途**：环境检查脚本
- **检查项**：
  - Python是否安装
  - frida包是否安装
  - frida-server是否运行
  - QQ Music是否运行
  - 输入/输出目录是否存在

---

## 技术架构

### 工作流程

```
1. 启动服务阶段
   ├─ 启动 frida-server.exe（管理员权限）
   └─ 启动 QQ Music 客户端（已登录VIP）

2. 连接阶段
   ├─ Python脚本连接到frida-server
   ├─ frida附加到QQ Music进程（QQMusic.exe）
   └─ 加载hook_qq_music.js脚本

3. 扫描阶段
   ├─ 扫描输入目录（G:\QQMusic\Download）
   └─ 查找所有.mflac和.mgg文件

4. 解密阶段（每个文件）
   ├─ 检查文件是否已转换（跳过已存在的）
   ├─ 调用Frida hook脚本解密
   ├─ QQ Music原生函数解密文件
   ├─ 写入临时文件
   ├─ 重命名为最终文件名
   ├─ 验证文件完整性
   └─ 失败则重试（最多3次）

5. 完成阶段
   ├─ 生成统计信息（JSON格式）
   ├─ 显示执行摘要
   └─ 保存详细日志
```

### Frida Hook机制

```
Python进程
   ↓ attach
QQ Music进程（QQMusic.exe）
   ↓ hook
QQMusicCommon.dll
   ↓ 调用
EncAndDesMediaFile类方法
   - Constructor: 创建对象
   - Open: 打开加密文件
   - GetSize: 获取文件大小
   - Read: 读取解密后的数据
   - Destructor: 销毁对象
```

---

## 文件格式转换

### 输入格式

| 扩展名 | 说明 | 示例 |
|--------|------|------|
| .mflac | 加密的FLAC格式 | 歌曲名.mflac |
| .mgg | 加密的OGG格式 | 歌曲名.mgg |

### 输出格式

| 输入扩展名 | 输出扩展名 | 音质 |
|------------|------------|------|
| .mflac | .flac | 无损 |
| .mgg | .ogg | 有损 |

---

## 使用说明

### 首次使用（5分钟）

1. 安装依赖
   ```batch
   双击运行 install_dependencies.bat
   ```

2. 下载frida-server
   - 访问：https://github.com/frida/frida/releases
   - 下载：frida-server-16.7.10-windows-x86_64.exe.xz
   - 解压到项目目录，重命名为frida-server.exe

3. 启动必要服务
   ```batch
   右键 start_frida_server.bat → 以管理员身份运行
   （保持窗口打开）
   启动QQ Music客户端（确保已登录VIP）
   ```

4. 开始解密
   ```batch
   双击运行 auto_decrypt.bat
   ```

### 日常使用（1分钟）

```batch
1. 确保frida-server和QQ Music正在运行
2. 运行 auto_decrypt.bat
3. 等待转换完成
```

### 命令行参数

```bash
# 基本使用
python main_cli.py

# 指定输入输出目录
python main_cli.py --input "D:\Music" --output "D:\Output"

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

---

## 目录结构

```
D:\WorkDev\qqmusic_decryptor\
├── main_cli.py                    # CLI核心工具（555行）
├── config.ini                     # 配置文件
├── requirements.txt               # Python依赖（frida==16.7.10）
├── hook_qq_music.js               # Frida解密脚本（120行）
│
├── auto_decrypt.bat               # 主批处理脚本
├── check_env.bat                  # 环境检查脚本
├── install_dependencies.bat       # 依赖安装脚本
├── start_frida_server.bat         # Frida服务启动脚本
│
├── gui_backup\                    # GUI备份版本
│   ├── main_gui.py               # GUI主程序
│   ├── hook_qq_music.js          # Hook脚本
│   ├── run_gui.bat               # GUI启动脚本
│   └── README.md                 # GUI文档
│
├── logs\                          # 日志目录
│   ├── decrypt.log               # 详细日志
│   └── stats.json                # 统计信息（JSON格式）
│
├── frida-server.exe               # Frida服务器（需手动下载）
├── frida-server-16.7.10-windows-x86_64.exe.xz  # 压缩包
│
├── README.md                      # 完整文档（271行）
├── QUICKSTART.md                  # 快速开始指南（180行）
├── PROJECT_SUMMARY.md             # 项目总结（316行）
│
└── 多个修复脚本...                 # 用于修复常见问题
```

---

## 日志和统计

### 日志文件（logs/decrypt.log）

格式：
```
[2026-01-25 14:30:45] [INFO] QQ Music 批量解密工具 - CLI版本
[2026-01-25 14:30:45] [INFO] 输入目录: G:\QQMusic\Download
[2026-01-25 14:30:45] [INFO] 输出目录: G:\QQMusic\Decrypted
[2026-01-25 14:30:46] [INFO] 找到 30 个加密文件
[2026-01-25 14:30:47] [INFO] 正在解密: 梁博 - 今天.mflac
[2026-01-25 14:30:50] [INFO] ✓ 解密成功: 梁博 - 今天.flac
```

### 统计文件（logs/stats.json）

```json
{
  "timestamp": "2026-01-25T14:30:45",
  "input_dir": "G:\QQMusic\Download",
  "output_dir": "G:\QQMusic\Decrypted",
  "stats": {
    "total": 30,
    "success": 28,
    "failed": 2,
    "skipped": 0,
    "start_time": 1706177445,
    "end_time": 1706185645,
    "duration": 8200,
    "speed": 1.95,
    "failed_files": [...]
  }
}
```

---

## 常见问题

### 1. 提示"Python未安装"
**解决**：访问 https://www.python.org/downloads/ 下载安装Python 3.8+

### 2. 提示"frida包未安装"
**解决**：
```bash
pip install -r requirements.txt
```

### 3. 提示"frida-server未运行"
**解决**：右键 start_frida_server.bat → 以管理员身份运行

### 4. 提示"QQ Music未运行"
**解决**：启动QQ Music客户端，确保已登录VIP账号

### 5. 提示"版本不匹配"
**解决**：确保frida和frida-server版本都是16.7.10

### 6. 解密失败
**可能原因**：
- QQ Music未运行或已断开连接
- 网络连接问题
- VIP账号权限问题

**解决方法**：
- 检查QQ Music是否正常运行
- 重新下载失败的文件
- 查看日志文件：logs\decrypt.log

---

## 性能指标

| 指标 | 预期值 |
|------|--------|
| 转换成功率 | ≥95% (28/30) |
| 目录结构保留 | 100% |
| 元数据完整性 | 100% |
| 平均转换速度 | 1.5-2个文件/分钟 |
| 内存占用 | <300MB |
| CPU占用 | 10-30% |
| 单文件转换时间 | 30-40秒 |

---

## 故障排除脚本

项目中包含多个测试和诊断脚本，用于环境检查和问题诊断：

- check_status.py：检查GUI文件状态
- diagnose_frida.py：诊断Frida连接问题
- test_frida.py：测试Frida连接
- diagnose_gui.py：环境诊断脚本
- check_current_paths.py：路径检查脚本
- test_gui_config.py：配置验证脚本
- test_gui_functions.py：功能测试脚本
- start_gui_directly.py：直接启动测试

---

## 依赖说明

### Python依赖（requirements.txt）

```
frida==16.7.10
```

### 外部依赖

1. **frida-server**
   - 版本：16.7.10
   - 下载地址：https://github.com/frida/frida/releases
   - 平台：Windows x86_64
   - 必须与frida包版本完全一致

2. **QQ Music客户端**
   - 需要已登录VIP账号
   - 必须正常运行

---

## 安全注意事项

1. **仅用于学习交流**：本工具仅供个人学习使用
2. **遵守法律**：请遵守相关法律法规
3. **VIP账号**：需要有效的QQ音乐VIP账号
4. **管理员权限**：frida-server需要以管理员身份运行

---

## 备用方案

如果CLI版本出现问题，可以使用GUI版本：

```batch
cd D:\WorkDev\qqmusic_decryptor\gui_backup
run_gui.bat
```

GUI版本提供图形界面，更易于调试和操作。

---

## 参考资料

- [Frida官方文档](https://frida.re/docs/)
- [strelitzia-reg/qqmusic-decryptor](https://github.com/strelitzia-reg/qqmusic-decryptor) - GUI版本参考
- [QQMusicCommon.dll](QQMusicCommon.dll) - QQ Music加密解密库

---

## 更新日志

### v1.0.0 (2026-01-25)
- ✅ 初始版本发布
- ✅ 支持批量解密.mflac/.mgg文件
- ✅ 保留原始目录结构
- ✅ 智能跳过已转换文件
- ✅ 错误重试机制
- ✅ 详细日志记录
- ✅ 统计信息保存

---

## 贡献

如有问题或建议，欢迎提交Issue或Pull Request。

---

## 许可证

本项目仅供学习交流使用，请遵守相关法律法规。

---

**最后更新**：2026-01-25
