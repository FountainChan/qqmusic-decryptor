---
title: refactor: Restructure project layout for open-source readiness
type: refactor
status: active
date: 2026-05-08
origin: docs/brainstorms/2026-05-08-project-restructure-requirements.md
---

# 项目结构重构 — 实施计划

## Overview

将散落在根目录的源码、GUI、第三方二进制按标准布局重新组织，为开源分享做准备。

## Problem Frame

当前项目文件全部平铺在根目录，源码(.py/.js)、入口脚本(.sh/.bat)、第三方二进制(frida-server.exe)、历史遗留脚本(drops/)混杂。开源分享时需要干净的标准项目布局。

## Requirements Trace

- R1. 所有 Python 源码和 JS Hook 脚本移入 `src/` 目录
- R2. `gui_backup/` 重命名为 `src/gui/`
- R3. `frida-server.exe` 移入 `three-party/` 目录
- R4. 入口脚本（`.sh` / `.bat`）保留在根目录
- R5. `config.ini`、`requirements.txt` 保留在根目录
- R6. 删除 `drops/` 目录
- R7. 所有入口脚本中的路径引用更新为新位置
- R8. Python 内部跨模块导入路径适配

## Scope Boundaries

- 不改动 Python 脚本的函数逻辑和参数接口
- 不改动 Frida Hook 脚本内容
- 不改动 `doc/` 目录结构
- 不改动 `AGENTS.md` 内容

## Context & Research

### Relevant Code and Patterns

- `gui_backup/main_gui.py` 已有 `sys.path.insert` 处理导入路径的模式，可复用
- 各入口脚本均使用硬编码相对路径引用 `gui_backup/` 或 `main_cli.py`，改一处即可

### Key Technical Decisions

- [方案B - 全部源码入 src/]: `gui/` 作为 `src/gui/` 子目录，保持导入路径统一
- [sys.path 适配]: 不依赖 `PYTHONPATH` 环境变量，直接在 Python 脚本中 `sys.path.insert` 确保无环境依赖
- [frida-server 入 three-party/]: 不使用常见的 `vendor/` 或 `bin/`，`three-party/` 语义更清晰

## Implementation Units

- [ ] **Unit 1: 目录创建与文件移动**

**Goal:** 创建目标目录结构，将文件移动到新位置

**Requirements:** R1, R2, R3, R6

**Dependencies:** None

**Approach:**
- 创建 `src/`、`three-party/` 目录
- 复制 `gui_backup/` → `src/gui/`（整个目录）
- 移动 `main_cli.py`、`supplement_album_metadata.py`、`metadata_utils.py`、`qqmusic_api_client.py`、`hook_qq_music.js` 到 `src/`
- 移动 `frida-server.exe` 到 `three-party/`
- 删除旧的 `gui_backup/` 目录
- 删除 `drops/` 目录

**Verification:**
- `ls src/` 应看到所有 .py 和 .js 文件
- `ls src/gui/` 应看到 main_gui.py 等
- `ls three-party/` 应看到 frida-server.exe
- `gui_backup/` 已不存在
- `drops/` 已不存在

- [ ] **Unit 2: 更新 Shell 入口脚本路径 (.sh)**

**Goal:** 所有 `.sh` 入口脚本中的路径引用指向新位置

**Requirements:** R4, R7

**Dependencies:** Unit 1

**Files:**
- Modify: `run_gui_simple.sh`
- Modify: `start_gui.sh`
- Modify: `run_supplement.sh`
- Modify: `auto_decrypt.sh`
- Modify: `start_frida_server.sh`
- Modify: `check_env.sh`

**Approach:**
- `run_gui_simple.sh`: `python gui_backup/main_gui.py` → `python src/gui/main_gui.py`
- `start_gui.sh`: `GUI_FILE="gui_backup/main_gui.py"` → `GUI_FILE="src/gui/main_gui.py"`
- `run_supplement.sh`: `supplement_album_metadata.py` → `src/supplement_album_metadata.py`
- `auto_decrypt.sh`: `main_cli.py` → `src/main_cli.py`
- `start_frida_server.sh`: `./frida-server.exe` → `./three-party/frida-server.exe`
- `check_env.sh`: `gui_backup` 目录检测改为 `src/gui`

**Verification:**
- 每个修改过的 `.sh` 文件 `grep "gui_backup\|\./frida-server"` 应返回空

- [ ] **Unit 3: 更新 Batch 入口脚本路径 (.bat)**

**Goal:** 所有 `.bat` 入口脚本中的路径引用指向新位置

**Requirements:** R4, R7

**Dependencies:** Unit 1

**Files:**
- Modify: `run_gui_simple.bat`
- Modify: `start_gui_english.bat`
- Modify: `run_supplement.bat`
- Modify: `auto_decrypt.bat`
- Modify: `start_frida_server.bat`
- Modify: `check_env.bat`
- Modify: `install_dependencies.bat`

**Approach:**
- 所有 `gui_backup\` 替换为 `src\gui\`
- 所有 `main_cli.py` 替换为 `src\main_cli.py`
- 所有 `supplement_album_metadata.py` 替换为 `src\supplement_album_metadata.py`
- `start_frida_server.bat`: `frida-server.exe` → `three-party\frida-server.exe`
- `check_env.bat`: `gui_backup` 目录检测改 `src\gui`

**Verification:**
- 每个修改过的 `.bat` 文件 `grep "gui_backup\|frida-server.exe"` 仅应出现三次方路径引用

- [ ] **Unit 4: 修复 Python 内部导入路径**

**Goal:** 确保移动到 `src/` 和 `src/gui/` 后的 Python 跨模块导入正常工作

**Requirements:** R8

**Dependencies:** Unit 1

**Files:**
- Modify: `src/gui/main_gui.py`
- Modify: `src/main_cli.py`
- Modify: `src/supplement_album_metadata.py`
- Modify: `src/metadata_utils.py`
- (if needed) `src/qqmusic_api_client.py`

**Approach:**
- `src/gui/main_gui.py`: 现有 `sys.path.insert(0, os.path.dirname(os.path.dirname(...)))` 是在 gui_backup/ 时向上两级的逻辑。改为 `sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))`，即指向 `src/` 目录
- `src/main_cli.py`: 已有的 `from metadata_utils import ...` 需要 `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` 将 `src/` 加入路径
- `src/supplement_album_metadata.py`: 同上，加入 sys.path 适配
- `src/metadata_utils.py`: `from qqmusic_api_client import ...` 需要同样的处理

**Patterns to follow:**
- `main_gui.py` 现有的 `sys.path.insert` 模式就是正确的范例

**Verification:**
- `PYTHONIOENCODING=utf-8 python -c "import py_compile; py_compile.compile('src/main_cli.py', doraise=True)"` 通过
- `PYTHONIOENCODING=utf-8 python -c "import py_compile; py_compile.compile('src/gui/main_gui.py', doraise=True)"` 通过
- `PYTHONIOENCODING=utf-8 python src/supplement_album_metadata.py --help` 正常输出

## System-Wide Impact

- **导入路径一致性**: 所有 Python 脚本内部导入将被统一处理，避免未来新增文件时遗漏
- **入口脚本引用**: 所有 shell/batch 入口均需同步更新，若有遗漏则对应功能不可用
- **AGENTS.md 目录结构部分**: 记录的是旧结构，但 scope 声明不修改其内容
- **doc/index.md 快速导航**: 中的路径引用也需要更新

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| 遗漏某处路径引用导致入口脚本失效 | Unit 2/3 逐文件修改后用 grep 验证无遗留旧路径 |
| Python 导入路径遗漏导致运行时 import 失败 | Unit 4 逐文件检查 import，语法验证通过即满足 |
| `gui_backup/main_gui.py` 中 `endswith('gui_backup')` 自检逻辑 | 改为 `endswith(('gui_backup', 'gui'))`，确保新路径也能正确计算项目根目录 |
