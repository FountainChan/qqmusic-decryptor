# 测试脚本管理和验证指南

**创建时间**：2026-01-29
**版本**：v1.0
**状态**：✅ 活跃

---

## 📋 测试脚本清单

### ✅ 保留的测试脚本

| 测试脚本 | 类型 | 用途 | 状态 |
|---------|------|------|------|
| `test/test_script.bat` | 批处理 | 验证基础逻辑 | ✅ 保留 |
| `test/test_api_standalone.py` | Python | API 独立测试 | ✅ 保留 |
| `test/test_api_structure.py` | Python | API 结构测试 | ✅ 保留 |

### ❓ 可删除的测试脚本

| 测试脚本 | 类型 | 用途 | 建议 |
|---------|------|------|------|
| `test/test_api_client_instance.py` | Python | API 客户端测试 | ❓ 可删除 |

---

## 🎯 测试脚本用途

### 1. test_script.bat ⭐ 重要

**用途**：验证批处理基础逻辑

**测试内容**：
- ✅ 验证 echo 命令是否显示
- ✅ 验证变量是否正确展开
- ✅ 验证 Python 命令是否正确构建
- ✅ 验证路径变量是否正确扩展

**使用场景**：
```bash
# Windows CMD
cd /d/WorkDev/qqmusic_decryptor\test
test_script.bat

# Git Bash
bash test/test_script.bat
```

**预期输出**：
```
[TEST 1] This is test line 1
[TEST 2] This is test line 2
[TEST 3] This is test line 3

[TEST 4] Python check...
[TEST 5] Python found OK
[TEST 6] Run Python script...

[TEST 7] Script execution completed
```

---

### 2. test_api_standalone.py

**用途**：独立测试 API 调用和响应

**测试内容**：
- ✅ 验证 API 是否可访问
- ✅ 验证 API 响应结构
- ✅ 验证 aDate 字段是否正确返回
- ✅ 验证日期格式是否正确（YYYY-MM-DD）

**使用场景**：
```bash
cd /d/WorkDev/qqmusic_decryptor\test
python test_api_standalone.py
```

**预期输出**：
```
============================================================
API Independent Test
============================================================

[TEST 1] API Connection: 200
[TEST 2] Response structure: dict_keys(['response', 'data'])
[TEST 2] aDate field: 2015-06-11

[OK] All tests passed

Press Enter to exit...
```

---

### 3. test_api_structure.py

**用途**：测试 API 响应的数据结构

**测试内容**：
- ✅ 验证 API 响应的嵌套结构
- ✅ 验证正确的字段访问路径
- ✅ 验证 aDate 字段的数据类型

**使用场景**：
```bash
cd /d/WorkDev/qqmusic_decryptor\test
python test_api_structure.py
```

---

## 🚀 如何使用测试脚本

### 场景 1：修改批处理文件后验证

**步骤**：
1. 修改 `run_supplement.bat`
2. 运行 `test/test_script.bat` 验证语法
3. 如果测试失败，修复批处理文件
4. 重复直到测试通过

**示例**：
```bash
# 1. 编辑 run_supplement.bat
# 2. 验证语法
test/test_script.bat

# 3. 如果测试失败，检查并修复
# 4. 验证通过后运行主脚本
run_supplement.bat
```

---

### 场景 2：修改 Python 脚本后验证

**步骤**：
1. 修改 `supplement_album_metadata.py`
2. 运行 `test/test_api_standalone.py` 验证 API
3. 如果测试失败，修复 Python 脚本
4. 运行主脚本验证完整功能

**示例**：
```bash
# 1. 编辑 supplement_album_metadata.py
# 2. 验证 API
test/test_api_standalone.py

# 3. 如果测试失败，检查并修复
# 4. 验证通过后运行主脚本
run_supplement.bat "G:\QQMusic\Decrypted\VipSongsDownload\专辑名"
```

---

## 🧪 测试脚本组织

### 目录结构

```
D:\WorkDev\qqmusic_decryptor\
├── test/                           # 测试脚本目录
│   ├── test_script.bat           # 批处理基础测试
│   ├── test_api_standalone.py   # API 独立测试
│   ├── test_api_structure.py      # API 结构测试
│   ├── test_api_client_instance.py # API 客户端测试
│   └── README.md               # 测试脚本说明（本文件）
│
├── run_supplement.bat             # 主脚本（批处理）
├── run_supplement.sh              # 主脚本（Shell）
├── supplement_album_metadata.py    # Python 主脚本
└── ...
```

---

## 📝 测试脚本编写规范

### 批处理测试脚本

**命名规范**：
- ✅ 使用 `test_<功能>.bat` 格式
- ✅ 放在 `test/` 目录中
- ✅ 包含清晰的测试步骤编号

**内容规范**：
```batch
@echo off
REM Test Script: <测试目的>
REM Created: <创建日期>
REM Author: <作者>

REM 测试步骤 1: <描述>
echo [TEST 1] <测试描述>
<测试命令 1>

REM 测试步骤 2: <描述>
echo [TEST 2] <测试描述>
<测试命令 2>

REM 显示测试结果
echo.
echo Test Completed.
pause
```

**成功标准**：
- 所有测试步骤都执行
- 没有错误或异常
- 输出清晰的测试结果

### Python 测试脚本

**命名规范**：
- ✅ 使用 `test_<功能>.py` 格式
- ✅ 放在 `test/` 目录中
- ✅ 包含详细的测试函数

**内容规范**：
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：<测试目的>
创建时间：<创建日期>
作者：<作者>
"""

import sys
import requests

def test_<功能>_1():
    """测试功能 1"""
    try:
        # 测试代码
        result = perform_action()
        print(f"[TEST 1] Success: {result}")
        return True
    except Exception as e:
        print(f"[TEST 1] Failed: {e}")
        return False

def test_<功能>_2():
    """测试功能 2"""
    try:
        # 测试代码
        result = perform_action()
        print(f"[TEST 2] Success: {result}")
        return True
    except Exception as e:
        print(f"[TEST 2] Failed: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("Test Script: <测试目的>")
    print("="*60)
    print()
    
    # 运行所有测试
    all_tests = [
        test_<功能>_1(),
        test_<功能>_2(),
    ]
    
    success_count = sum(1 for test in all_tests if test)
    total_count = len(all_tests)
    
    print()
    if success_count == total_count:
        print(f"[OK] All tests passed ({success_count}/{total_count})")
    else:
        print(f"[FAIL] Some tests failed ({success_count}/{total_count})")
    
    print()
    input("Press Enter to exit...")
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
```

**成功标准**：
- 所有测试函数都执行
- 没有未捕获的异常
- 显示清晰的测试结果和统计

---

## 🧪 删除测试脚本的标准

### ✅ 保留的标准

- **通用测试工具**：可以被多个项目或功能复用
  - 示例：`test_script.bat`, `test_api_standalone.py`
- **保留理由**：基础测试，不会过时，每次修改都需要验证

- **核心功能测试**：验证项目的主要功能
  - 示例：`test_api_structure.py`
  - **保留理由**：核心功能，持续需要验证

- **正在调试的测试**：用于当前正在解决的问题
  - 示例：任何以 `debug_` 开头的测试
  - **保留理由**：问题未解决，需要持续测试

### ❓ 可删除的标准

- **一次性测试**：完成特定调试任务后，不再需要
  - 示例：`test_api_client_instance.py`
  - **删除理由**：功能已被其他测试覆盖

- **重复的测试**：功能已被其他测试覆盖
  - 示例：多个测试相同功能的脚本
  - **删除理由**：避免维护重复代码

- **过时的测试**：测试的功能已更改或不再存在
  - 示例：测试已删除的功能
  - **删除理由**：清理过时代码

---

## 🎯 测试脚本使用流程

### 1. 创建测试脚本

**步骤**：
1. 确定需要测试的功能
2. 选择合适的测试类型（批处理或 Python）
3. 编写测试脚本（遵循上述规范）
4. 放入 `test/` 目录
5. 添加测试文档到 `test/README.md`

### 2. 运行测试脚本

**步骤**：
1. 打开命令提示符（CMD 或 Git Bash）
2. 进入 `test/` 目录
3. 运行测试脚本
4. 检查测试结果
5. 如果失败，分析并修复问题

### 3. 验证修复

**步骤**：
1. 根据测试结果修复问题
2. 重新运行测试脚本
3. 验证测试通过
4. 运行主脚本验证完整功能

---

## 📊 测试脚本统计

### 当前测试脚本统计

| 类别 | 数量 | 占比 |
|------|------|------|
| 保留的测试脚本 | 3 | 75% |
| 可删除的测试脚本 | 1 | 25% |
| 总计 | 4 | 100% |

---

## 🔄 版本历史

### v1.0 (2026-01-29)
- ✅ 创建测试脚本指南
- ✅ 整理现有测试脚本到 `test/` 目录
- ✅ 制定测试脚本编写规范
- ✅ 建立删除测试脚本的标准

---

## 🚀 快速开始

### 创建新测试

1. 确定 测试目的
2. 选择测试类型（批处理/Python）
3. 编写测试脚本（遵循规范）
4. 放入 `test/` 目录

### 运行现有测试

```bash
# 批处理测试
cd /d/WorkDev/qqmusic_decryptor\test
test_script.bat

# Python 测试
cd /d/WorkDev/qqmusic_decryptor\test
python test_api_standalone.py
```

### 删除不需要的测试

```bash
# 确认测试不再需要
# 确认没有其他测试依赖它
# 手动删除
rm test/test_api_client_instance.py
```

---

## 📚 相关文档

- **主文档**：`AGENTS.md` - AI 助手规则和最佳实践
- **实施报告**：`doc/DATE_FIX_COMPLETION_REPORT.md` - 功能完成报告
- **使用指南**：`doc/RUN_SCRIPT_GUIDE.md` - 脚本使用指南

---

**文档创建时间**：2026-01-29
**最后更新**：2026-01-29
**维护者**：AI 助手
