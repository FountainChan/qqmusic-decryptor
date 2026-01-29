# QQ音乐解密工具技能

## 技能描述

这是一个基于 Frida 动态插桩技术的 QQ 音乐批量解密工具，用于将 QQ 音乐的加密音乐文件（`.mflac`/`.mgg`）转换为标准格式（`.flac`/`.ogg`）。

## 触发关键词

当你说以下任一关键词时，此技能将被激活：
- 转换音乐
- 解密音乐
- 解码音乐
- 转换flac
- 转换ogg
- 解密mflac
- 解密mgg

## 前置条件

使用前需要确保：

1. **Python 环境**：Python 3.8+ 已安装
2. **依赖包**：
   - frida==16.7.10
   - mutagen>=1.47.0
   - 运行 `install_dependencies.bat` 安装

3. **frida-server 运行中**：
   - 以管理员身份运行 `start_frida_server.bat`
   - 保持窗口打开状态

4. **QQ Music 运行中**：
   - 启动 QQ Music 客户端
   - 已登录 VIP 账号

## 执行步骤

### 方式一：GUI 模式（推荐）

1. 运行 `run_gui_simple.bat`
2. 在 GUI 界面中配置输入/输出目录
3. 点击"开始解密"按钮
4. 等待解密完成

### 方式二：CLI 模式

1. 确保 frida-server 和 QQ Music 运行中
2. 运行 `auto_decrypt.bat`
3. 等待批量解密完成

## 功能特性

- ✅ 批量解密 .mflac/.mgg 文件
- ✅ 保留原始目录结构
- ✅ 自动复制 .lrc 歌词文件
- ✅ 自动添加音轨号元数据（从文件名提取）
- ✅ 智能跳过已转换文件
- ✅ 错误重试机制（最多3次）
- ✅ 详细日志记录
- ✅ 统计信息保存

## 输入输出格式

| 输入格式 | 输出格式 | 音质 |
|----------|----------|------|
| .mflac | .flac | 无损 |
| .mgg | .ogg | 有损 |

## 默认路径

- 输入目录：`G:\QQMusic\Download`
- 输出目录：`G:\QQMusic\Decrypted\VipSongsDownload`

## 故障排除

### 问题：一闪而过
**解决**：
- 检查 frida-server 是否运行（管理员权限）
- 检查 QQ Music 是否运行并登录 VIP
- 查看日志文件：`logs/decrypt.log`

### 问题：找不到 mutagen
**解决**：
```bash
pip install mutagen
```

### 问题：版本不匹配
**解决**：
- 确保 frida 和 frida-server 版本都是 16.7.10

## 文件位置

- 项目目录：`D:\WorkDev\qqmusic_decryptor`
- 主程序：`main_cli.py`（CLI）、`gui_backup/main_gui.py`（GUI）
- 配置文件：`config.ini`
- 文档目录：`doc/`
- 日志目录：`logs/`

## 快速开始

```batch
# 1. 启动 frida-server（需要管理员权限）
start_frida_server.bat

# 2. 启动 QQ Music 并登录 VIP

# 3. 启动解密工具
run_gui_simple.bat

# 4. 在 GUI 中配置路径并开始解密
```

## 性能指标

- 转换成功率：≥95%
- 平均速度：1.5-2个文件/分钟
- 单文件时间：30-40秒
- 内存占用：<300MB

## 安全说明

本工具仅供个人学习使用，请遵守相关法律法规。
