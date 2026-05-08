---
date: 2026-05-08
topic: project-restructure
---

# 项目结构重构 — 需求文档

## Problem Frame

当前项目文件散落在根目录，源码、入口脚本、第三方二进制混杂。为开源分享准备，需要标准化项目布局。

## Requirements

**目录重组**
- R1. 所有 Python 源码和 JS Hook 脚本移入 `src/` 目录
- R2. `gui_backup/` 重命名为 `src/gui/`
- R3. `frida-server.exe` 移入 `three-party/` 目录
- R4. 入口脚本（`.sh` / `.bat`）保留在根目录
- R5. `config.ini`、`requirements.txt` 保留在根目录

**清理**
- R6. 删除 `drops/` 目录（遗留修复脚本）
- R7. 删除已清理过的测试脚本产生的 `__pycache__/` 缓存

**导入路径修复**
- R8. 所有入口脚本中对 `gui_backup/` 的路径引用改为 `src/gui/`
- R9. `start_frida_server.*` 中对 `frida-server.exe` 的路径引用改为 `three-party/frida-server.exe`
- R10. Python 内部跨模块导入（如 main_gui.py 引用 metadata_utils）需适配新路径

## Success Criteria

- `bash run_supplement.sh` 正常运行
- `bash run_gui_simple.sh` / `bash start_gui.sh` GUI 正常启动
- `bash auto_decrypt.sh` CLI 正常启动
- `bash check_env.sh` 环境检查通过
- 根目录 `.md` 链接/文件引用指向正确的新路径

## Scope Boundaries

- 不改动 Python 脚本的函数逻辑、参数接口
- 不改动 Frida Hook 脚本
- 不改动 `doc/` 目录结构（已在之前整理完成）
- 不改动 `AGENTS.md` 内容

## Key Decisions

- [方案B] 全部源码压入 `src/`，而非 `src/`+`gui/` 分离：简化导入链
- [保留根目录] `config.ini` 和 `requirements.txt` 留在根目录：符合开源惯例
- [删除 drops/] 遗留修复脚本已无实际用途，开源后更不应保留

## Dependencies / Assumptions

- Python 的模块导入路径适配可通过 `sys.path.insert` 或入口脚本中设置 `PYTHONPATH` 解决
- 各入口脚本原有的暂停/等待/错误处理逻辑不因路径变更受影响

## Outstanding Questions

### Deferred to Planning
- [Affects R10][Technical] Python 导入路径的具体适配方案（sys.path vs PYTHONPATH）
- [Affects R8-R9][Needs research] `check_env.sh` 中 `gui_backup` 目录检测逻辑的替换方案
