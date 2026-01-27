# Claude AI 项目集成文档

## 项目标识

**项目名称**：QQ Music 批量解密工具  
**项目类型**：桌面应用工具 / 命令行工具  
**主要语言**：Python, JavaScript, Batch  
**技术栈**：Frida动态插桩, Tkinter, Python CLI

---

## Claude AI 集成指南

本指南旨在帮助Claude AI理解、维护和改进此项目。

---

## 项目概览

### 核心目的
开发一个自动化工具，用于批量解密QQ音乐的加密音频文件（.mflac/.mgg格式），将其转换为标准格式（.flac/.ogg），同时保留原始目录结构和元数据。

### 关键特性
- 使用Frida动态插桩技术hook QQ Music进程
- 调用QQ Music原生解密函数
- 支持CLI和GUI两种界面
- 智能文件跳过和错误重试机制
- 详细的日志记录和统计信息

---

## Claude AI 知识库

### 1. 技术架构理解

#### Frida Hook机制
```javascript
// hook_qq_music.js 核心逻辑
// 1. 找到QQMusicCommon.dll中的目标函数
// 2. 创建NativeFunction包装器
// 3. 分配内存并调用解密函数
// 4. 分块读取解密数据（64KB/次）
// 5. 写入到临时文件并重命名
```

#### Python CLI架构
```python
# main_cli.py 核心类结构
class QQMusicDecryptorCLI:
    - connect_to_qqmusic()     # 连接到QQ Music进程
    - load_decrypt_script()    # 加载Frida脚本
    - decrypt_file()           # 解密单个文件
    - decrypt_all()            # 批量解密
    - verify_flac_file()       # 验证文件完整性
    - save_stats()             # 保存统计信息
```

---

## Claude AI 使用场景

### 场景1：代码理解与分析

**任务**：解释main_cli.py的工作流程

**Claude响应**：
```
main_cli.py 的工作流程：

1. 初始化阶段
   - 加载配置文件 (config.ini)
   - 解析命令行参数
   - 设置日志系统

2. 连接阶段
   - 查找QQ Music进程 (使用tasklist命令)
   - 使用frida.attach()附加到进程
   - 加载并执行hook_qq_music.js脚本

3. 扫描阶段
   - 遍历输入目录
   - 查找所有.mflac和.mgg文件
   - 构建待处理文件列表

4. 解密阶段（每个文件）
   - 计算输出路径（保留目录结构）
   - 检查文件是否已转换
   - 调用Frida脚本的decrypt函数
   - 验证输出文件完整性
   - 失败则重试（最多3次）

5. 完成阶段
   - 生成统计信息
   - 保存到logs/stats.json
   - 显示执行摘要
   - 清理连接资源
```

### 场景2：问题诊断

**任务**：诊断"解密失败"问题

**Claude分析**：
```
可能的原因和排查步骤：

1. QQ Music进程未运行
   - 检查：tasklist | findstr QQMusic.exe
   - 解决：手动启动QQ Music客户端

2. frida-server未运行
   - 检查：tasklist | findstr frida-server.exe
   - 解决：以管理员身份运行start_frida_server.bat

3. 版本不匹配
   - 检查：python -c "import frida; print(frida.__version__)"
   - 解决：确保frida和frida-server都是16.7.10

4. VIP账号问题
   - 检查：QQ Music是否已登录VIP
   - 解决：重新登录或验证VIP状态

5. 文件路径问题
   - 检查：config.ini中的路径是否正确
   - 解决：修改input_dir和output_dir

6. Frida Hook失败
   - 查看日志：logs/decrypt.log
   - 检查：hook_qq_music.js是否正确加载
   - 验证：QQMusicCommon.dll中的函数地址

诊断命令：
  python diagnose_frida.py
  python test_frida.py
  check_env.bat
```

### 场景3：代码优化建议

**任务**：优化解密速度

**Claude建议**：
```
当前性能分析：
  - 单文件解密时间：30-40秒
  - 批量处理速度：1.5-2文件/分钟
  - 主要瓶颈：Frida RPC调用和文件IO

优化方案：

1. 减少Frida RPC调用开销
   - 在JavaScript端实现批量操作
   - 减少Python-JavaScript的通信次数

2. 优化文件IO
   - 使用更大的块大小（当前64KB）
   - 尝试使用异步IO
   - 考虑内存映射文件

3. 并行处理
   - 使用多线程处理多个文件
   - 注意：每个文件需要独立的frida会话

4. 缓存优化
   - 缓存QQ Music进程句柄
   - 避免重复的版本检查

代码修改建议：
  在hook_qq_music.js中增加chunkSize：
    var chunkSize = 0x40000;  // 256KB（原来是64KB）
  
  在main_cli.py中添加批处理：
    def decrypt_batch(self, files):
        # 实现批量解密逻辑
        pass

预期提升：
  - 速度提升：30-50%
  - 内存占用：可能增加20-30%
```

---

## Claude AI 代码修改指南

### 修改前检查清单

在修改代码前，Claude应检查：

1. **文件完整性**
   - 检查文件是否存在
   - 验证文件是否被修改过
   - 查看文件备份（.bak文件）

2. **依赖关系**
   - 识别被修改文件的依赖
   - 检查是否有其他文件引用此文件
   - 验证修改不会破坏现有功能

3. **配置一致性**
   - 检查config.ini是否需要更新
   - 确认路径配置的正确性
   - 验证日志配置

4. **测试覆盖**
   - 识别需要测试的场景
   - 创建测试用例
   - 验证修改不会引入bug

---

## Claude AI 故障排查流程

### 流程图

```
问题出现
   ↓
检查日志文件 (logs/decrypt.log)
   ↓
检查环境
   ├─ Python是否安装
   ├─ frida包是否安装
   ├─ frida-server是否运行
   └─ QQ Music是否运行
   ↓
检查配置 (config.ini)
   ├─ 路径是否正确
   ├─ 权限是否足够
   └─ 格式是否正确
   ↓
诊断工具
   ├─ 运行 check_env.bat
   ├─ 运行 diagnose_frida.py
   └─ 运行 test_frida.py
   ↓
根据结果采取行动
```

### 常见错误代码

| 错误代码 | 含义 | 解决方案 |
|---------|------|---------|
| ProcessNotFoundError | 未找到QQ Music进程 | 启动QQ Music客户端 |
| TimedOutError | 解密超时 | 增加超时时间或重试 |
| AttributeError | Frida脚本加载失败 | 检查hook_qq_music.js |
| PermissionError | 文件权限不足 | 以管理员身份运行 |
| FileNotFoundError | 文件不存在 | 检查路径配置 |

---

## Claude AI 性能基准

### 当前性能指标

| 操作 | 时间 | 备注 |
|------|------|------|
| 单文件解密（30MB） | 30-40秒 | 取决于文件大小 |
| 批量处理（30个文件） | 15-20分钟 | 包含重试时间 |
| 启动时间 | <5秒 | 包含连接和脚本加载 |
| 内存占用 | <300MB | 取决于并发数 |

### 性能优化目标

| 指标 | 当前值 | 目标值 | 改进 |
|------|--------|--------|------|
| 单文件解密 | 35秒 | 20秒 | +43% |
| 批量速度 | 1.8文件/分钟 | 3.0文件/分钟 | +67% |
| 内存占用 | 280MB | 200MB | -29% |

---

## Claude AI 安全注意事项

### 1. 权限管理

```python
# 验证管理员权限
import ctypes
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
```

### 2. 路径验证

```python
# 防止路径遍历攻击
def safe_path_join(base, path):
    """安全地连接路径"""
    full_path = os.path.abspath(os.path.join(base, path))
    return full_path if full_path.startswith(base) else None
```

### 3. 输入验证

```python
# 验证文件扩展名
ALLOWED_EXTENSIONS = {".mflac", ".mgg"}

def is_valid_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS
```

---

## Claude AI 版本管理

### 版本号格式

```
v主版本.次版本.修订号

例如：
- v1.0.0 - 初始版本
- v1.1.0 - 新增功能
- v1.1.1 - Bug修复
- v2.0.0 - 重大更新
```

---

## Claude AI 社区资源

### 相关项目

- [Frida官方仓库](https://github.com/frida/frida)
- [strelitzia-reg/qqmusic-decryptor](https://github.com/strelitzia-reg/qqmusic-decryptor)
- [Frida文档](https://frida.re/docs/)

---

## Claude AI 联系和支持

### 获取帮助

1. **查看文档**
   - README.md - 完整使用指南
   - QUICKSTART.md - 快速开始
   - PROJECT_SUMMARY.md - 项目总结

2. **运行诊断**
   - check_env.bat - 环境检查
   - diagnose_frida.py - Frida诊断
   - test_frida.py - Frida测试

3. **查看日志**
   - logs/decrypt.log - 详细日志
   - logs/stats.json - 统计信息

---

## 附录：常用命令速查

### Frida命令

```bash
# 列出所有进程
frida-ps -a

# 附加到进程
frida -l hook_qq_music.js QQMusic

# 查看Frida版本
frida --version
```

### Python命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行CLI工具
python main_cli.py --verbose

# 运行测试
python -m unittest test_decryption.py
```

### Batch命令

```batch
# 检查环境
check_env.bat

# 启动frida-server（管理员）
start_frida_server.bat

# 开始解密
auto_decrypt.bat
```

---

**文档版本**：v1.0.0  
**最后更新**：2026-01-26  
**维护者**：Claude AI

---

## 结语

本文档旨在为Claude AI提供全面的项目理解和使用指南。通过遵循本文档的指导，Claude AI可以更有效地理解、维护和改进QQ音乐解密工具项目。

如需进一步的信息或支持，请参考项目根目录下的其他文档文件。
