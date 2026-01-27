# 批处理文件换行符修复报告

**日期**: 2026-01-28
**问题**: run_gui_simple.bat 运行失败，显示字符截断错误

## 问题分析

### 错误日志
```
'ython' 不是内部或外部命令
'ho' 不是内部或外部命令
```

### 根本原因
批处理文件使用 LF (Unix) 换行符（`\n`），而不是 Windows 要求的 CRLF 换行符（`\r\n`）。

### 影响范围
所有批处理文件都存在此问题。

## 修复详情

### 修复的文件
- ✅ run_gui_simple.bat
- ✅ launch_gui.bat
- ✅ start_frida_server.bat
- ✅ auto_decrypt.bat
- ✅ install_dependencies.bat
- ✅ check_env.bat
- ✅ start_gui_english.bat
- ✅ run_diagnose_gui.bat

### 修复方法
使用 `sed 's/$/\r/'` 将 LF 转换为 CRLF

### 验证结果
```bash
file run_gui_simple.bat
# 输出: DOS batch file, Unicode text, UTF-8 text, with CRLF line terminators
```

## 经验总结

1. **Windows 批处理文件必须使用 CRLF 换行符**
   - LF: `\n` (0x0A) - Unix/Linux 换行符
   - CRLF: `\r\n` (0x0D 0x0A) - Windows 换行符

2. **创建批处理文件时的注意事项**
   - 使用支持 CRLF 的编辑器（Notepad++, VS Code 等）
   - 保存时选择 "CRLF" 换行符
   - 使用 UTF-8 编码（无 BOM）

3. **检测和修复命令**
   ```bash
   # 检测换行符
   file filename.bat

   # 修复换行符 (sed)
   sed 's/$/\r/' input.bat > output.bat

   # 修复换行符 (dos2unix 工具)
   unix2dos filename.bat
   ```

## AGENTS.md 更新

已在 `开发经验与最佳实践` 的 `批处理文件编码和编写规范` 中添加：

- **规则**：批处理文件必须使用 CRLF 换行符（\r\n）
- **原因**：Windows 批处理器只识别 CRLF，LF 会导致解析错误
- **最佳实践**：
  - 使用支持 CRLF 的编辑器
  - 保存时明确选择 CRLF 换行符
  - 使用 `file` 命令验证换行符类型
  - 使用 `sed 's/$/\r/'` 或 `unix2dos` 修复 LF 换行符

## 测试结果

- ✅ run_gui_simple.bat 换行符正确
- ✅ 所有批处理文件换行符已修复
- ✅ 可以正常启动 GUI
