# QQ Music 解密工具 - 文档索引

> 项目文档快速导航

**最后更新**: 2026-01-26
**项目路径**: `D:\WorkDev\qqmusic_decryptor`

---

## 📚 文档分类

### 📖 核心文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **项目说明** | `README.md` | 项目概述、功能介绍、快速开始 |
| **快速开始** | `QUICKSTART.md` | 5分钟快速上手指南 |
| **项目总结** | `PROJECT_SUMMARY.md` | 项目详细总结和架构说明 |

### 🔧 技术文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **Agents文档** | `agents.md` | 项目完整文档，面向所有用户 |
| **Claude文档** | `claude.md` | AI助手集成指南，面向开发者 |
| **Shell脚本指南** | `SHELL_SCRIPTS_GUIDE.md` | Git Bash 脚本使用指南 |
| **API文档** | `API.md` | (如需要) API接口说明 |

### 📋 问题解决

| 文档 | 路径 | 说明 |
|------|------|------|
| **问题解决记录** | `doc/problem_solved.md` | ⭐ 所有问题及其解决方案 |
| **测试报告** | `TEST_REPORT.md` | GUI修复的完整测试报告 |
| **GUI启动指南** | `GUI_STARTUP_GUIDE.md` | GUI使用详细说明 |

### 🐛 故障排除

| 脚本 | 路径 | 说明 |
|------|------|------|
| **配置检查** | `check_current_paths.py` | 检查当前GUI路径配置 |
| **环境诊断** | `diagnose_gui.py` | 诊断GUI启动环境 |
| **配置验证** | `test_gui_config.py` | 验证GUI配置是否正确 |
| **功能测试** | `test_gui_functions.py` | 测试GUI核心功能 |

---

## 🚀 快速导航

### 我想...

- **了解项目** → 阅读 `README.md`
- **快速开始** → 阅读 `QUICKSTART.md`
- **解决问题** → 阅读 `doc/problem_solved.md`
- **启动GUI（推荐）** → 双击 `run_gui_simple.bat`
- **启动GUI（Git Bash）** → 运行 `bash start_gui.sh`
- **诊断问题** → 运行 `python diagnose_gui.py`
- **检查环境** → 运行 `bash check_env.sh`
- **检查配置** → 运行 `python check_current_paths.py`

---

## 📊 问题解决快速参考

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| **输出目录错误** | 详见 `doc/problem_solved.md` - 问题1 |
| **目录结构未保留** | 详见 `doc/problem_solved.md` - 问题2 |
| **批处理文件乱码** | 使用 `run_gui_simple.bat` |
| **GUI启动失败** | 运行 `python diagnose_gui.py` |

### 快速修复

```bash
# 检查配置
python check_current_paths.py

# 测试功能
python test_gui_functions.py

# 诊断环境
python diagnose_gui.py

# 启动GUI（推荐）
# 双击: run_gui_simple.bat
```

---

## 📁 项目结构

```
D:\WorkDev\qqmusic_decryptor\
├── doc/                           # 📂 文档目录
│   ├── problem_solved.md          # 📝 问题解决记录
│   └── SHELL_SCRIPTS_GUIDE.md   # 📝 Shell脚本使用指南
│
├── gui_backup/                     # 📂 GUI备份版本
│   ├── main_gui.py                # GUI主程序（已修复）
│   └── main_gui.py.bak           # 原始备份
│
├── logs/                          # 📂 日志目录
│   ├── decrypt.log                # 解密日志
│   └── stats.json                # 统计信息
│
├── 核心文件
│   ├── main_cli.py                # CLI核心工具
│   ├── hook_qq_music.js           # Frida解密脚本
│   ├── config.ini                 # 配置文件
│   └── requirements.txt           # Python依赖
│
├── 启动脚本（.bat）
│   ├── run_gui_simple.bat         # ⭐ 推荐启动方式
│   ├── launch_gui.bat             # 标准启动方式
│   ├── start_frida_server.bat     # Frida服务启动
│   └── auto_decrypt.bat           # 自动解密脚本
│
├── 启动脚本（.sh）
│   ├── start_gui.sh              # GUI启动（Git Bash）
│   ├── start_frida_server.sh      # Frida服务启动（Git Bash）
│   ├── auto_decrypt.sh            # 自动解密（Git Bash）
│   └── check_env.sh              # 环境检查（Git Bash）
│
├── 测试脚本
│   ├── test_gui_config.py         # 配置验证
│   ├── test_gui_functions.py      # 功能测试
│   ├── diagnose_gui.py            # 环境诊断
│   └── check_current_paths.py     # 路径检查
│
└── 文档
    ├── README.md                  # 项目说明
    ├── QUICKSTART.md              # 快速开始
    ├── PROJECT_SUMMARY.md         # 项目总结
    ├── agents.md                 # Agents文档
    ├── claude.md                 # Claude文档
    ├── TEST_REPORT.md            # 测试报告
    ├── GUI_STARTUP_GUIDE.md      # GUI指南
    └── doc_index.md             # 本文件（文档索引）
```

---

## 🎯 使用场景

### 场景1: 首次使用

1. 阅读 `README.md` 了解项目
2. 阅读 `QUICKSTART.md` 快速开始
3. 运行 `install_dependencies.bat` 安装依赖
4. 启动 `start_frida_server.bat`（管理员权限）
5. 启动 QQ Music 客户端（登录VIP）
6. 运行 `run_gui_simple.bat` 启动GUI

### 场景2: 遇到问题

1. 阅读 `doc/problem_solved.md` 查找问题
2. 运行 `diagnose_gui.py` 诊断环境
3. 查看相关问题的解决方案
4. 应用修复方案
5. 运行测试脚本验证

### 场景3: 测试修复

1. 运行 `test_gui_config.py` 验证配置
2. 运行 `test_gui_functions.py` 验证功能
3. 查看 `TEST_REPORT.md` 了解测试结果
4. 启动GUI进行实际测试

### 场景4: 二次开发

1. 阅读 `agents.md` 了解项目架构
2. 阅读 `claude.md` 了解AI集成
3. 阅读 `PROJECT_SUMMARY.md` 了解技术细节
4. 查看 `gui_backup/main_gui.py` 源代码

---

## 📞 获取帮助

### 常见问题解决

1. **配置问题** → `doc/problem_solved.md`
2. **环境问题** → `python diagnose_gui.py`
3. **功能问题** → `test_gui_functions.py`
4. **启动问题** → `GUI_STARTUP_GUIDE.md`

### 查看测试结果

- 完整测试报告: `TEST_REPORT.md`
- 配置验证: `python test_gui_config.py`
- 功能测试: `python test_gui_functions.py`

### 备份和恢复

- 原始备份: `gui_backup/main_gui.py.bak`
- 恢复命令: 见 `doc/problem_solved.md`

---

## 🔍 文档更新记录

### v1.2 (2026-01-29)

**新增**:
- ✅ `doc/SHELL_SCRIPTS_GUIDE.md` - Shell脚本使用指南
- ✅ `start_gui.sh` - GUI启动脚本（Git Bash）
- ✅ `start_frida_server.sh` - Frida服务启动（Git Bash）
- ✅ `auto_decrypt.sh` - 自动解密脚本（Git Bash）
- ✅ `check_env.sh` - 环境检查脚本（Git Bash）

**更新**:
- ✅ 更新 `AGENTS.md` - 添加命令行工具使用规则
- ✅ 更新 `doc_index.md` - 添加Shell脚本相关内容

### v1.1 (2026-01-26)

**新增**:
- ✅ `doc/problem_solved.md` - 问题解决记录
- ✅ `doc_index.md` - 文档索引
- ✅ `TEST_REPORT.md` - 测试报告
- ✅ `GUI_STARTUP_GUIDE.md` - GUI指南

**更新**:
- ✅ 更新 `agents.md` - 完整项目文档
- ✅ 更新 `claude.md` - AI集成指南

### v1.0 (2026-01-25)

**初始版本**:
- ✅ `README.md` - 项目说明
- ✅ `QUICKSTART.md` - 快速开始
- ✅ `PROJECT_SUMMARY.md` - 项目总结

---

## 💡 使用建议

### 推荐阅读顺序

**初次使用者**:
1. `README.md` → 了解项目
2. `QUICKSTART.md` → 快速上手
3. `GUI_STARTUP_GUIDE.md` → 学习使用GUI

**遇到问题**:
1. `doc/problem_solved.md` → 查找问题
2. `TEST_REPORT.md` → 了解修复情况
3. `diagnose_gui.py` → 诊断环境

**开发者**:
1. `agents.md` → 了解架构
2. `claude.md` → AI集成
3. `PROJECT_SUMMARY.md` → 技术细节

### 文档维护

**何时更新文档**:
- ✅ 修复bug后
- ✅ 添加新功能后
- ✅ 改进现有功能后
- ✅ 发现新问题后

**更新内容**:
- 问题描述
- 解决方案
- 修复代码
- 测试结果

---

## 📊 快速命令参考

### Windows Batch
```batch
# 启动GUI
run_gui_simple.bat

# 诊断环境
diagnose_gui.py

# 检查配置
check_current_paths.py

# 测试配置
test_gui_config.py

# 测试功能
test_gui_functions.py

# CLI版本
python main_cli.py

# 自动解密
auto_decrypt.bat
```

### Git Bash（推荐）
```bash
# 启动GUI
cd /d/WorkDev/qqmusic_decryptor
bash start_gui.sh

# 检查环境
bash check_env.sh

# 启动frida-server
bash start_frida_server.sh

# 自动解密
bash auto_decrypt.sh

# CLI版本
python main_cli.py
```

---

## 🔗 相关资源

- [Frida官方文档](https://frida.re/docs/)
- [strelitzia-reg/qqmusic-decryptor](https://github.com/strelitzia-reg/qqmusic-decryptor)

---

## 📝 文档维护

**文档版本**: 1.1
**最后更新**: 2026-01-26
**维护者**: Claude AI Assistant

---

**注意**: 本文档索引可能会随着项目的发展而更新，请定期查看最新版本。
