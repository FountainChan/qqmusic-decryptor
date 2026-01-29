# QQ音乐解密技能说明

## 技能已创建

成功创建 QQ 音乐解密技能，可通过以下关键词触发：

### 触发关键词
- "转换音乐"
- "解密音乐"
- "解码音乐"
- "转换flac"
- "转换ogg"
- "解密mflac"
- "解密mgg"

## 使用方法

### 方式一：直接触发技能（推荐）
直接对我说：
```
请转换音乐
或
帮我解密音乐
或
开始解码音乐
```

AI 将自动：
1. 检查前置条件（Python、依赖、frida-server、QQ Music）
2. 启动 GUI 解密工具
3. 等待你配置路径并开始解密

### 方式二：手动运行
如果你想手动运行：

**启动 GUI**：
```batch
run_gui_simple.bat
```

**启动 CLI**：
```batch
auto_decrypt.bat
```

## 前置条件检查清单

使用前请确认：

- [ ] Python 3.8+ 已安装
- [ ] 依赖已安装（运行 `install_dependencies.bat`）
- [ ] frida-server 正在运行（管理员权限）
- [ ] QQ Music 客户端已启动
- [ ] QQ Music 已登录 VIP 账号

## 技能文件位置

- JSON 定义：`.skills/qqmusic_decryptor.json`
- Markdown 文档：`.skills/qqmusic_decryptor.md`

## 功能说明

此技能将自动：

1. **环境检查**：验证所有前置条件
2. **启动工具**：打开 GUI 界面
3. **等待配置**：让你选择输入/输出目录
4. **执行解密**：批量转换加密文件
5. **附加功能**：
   - 自动复制歌词文件
   - 自动添加音轨号元数据
   - 保留目录结构

## 故障排除

如果技能启动失败：

1. **检查 frida-server**
   - 右键 `start_frida_server.bat` → 以管理员身份运行
   - 保持窗口打开

2. **检查 QQ Music**
   - 确保 QQ Music 正在运行
   - 确保已登录 VIP

3. **检查依赖**
   - 运行 `install_dependencies.bat`
   - 运行 `pip install mutagen`

4. **查看日志**
   - 打开 `logs/decrypt.log`

## 快速开始示例

```
你: 转换音乐
AI: [检查环境] → [启动 GUI] → [等待配置]
你: [在 GUI 中设置路径并点击开始]
AI: [执行解密] → [显示进度] → [完成]
```

## 注意事项

- 解密速度：约 30-40秒/文件
- 需要网络：QQ Music 需要 VIP 验证
- 保持 frida-server 运行：整个解密过程
- 文件大小：确保有足够磁盘空间

## 进阶功能

除了基本的解密功能，还支持：

1. **目录结构保留**：自动复制文件夹结构
2. **歌词文件复制**：自动复制 .lrc 文件
3. **音轨号添加**：从文件名提取数字作为音轨号
4. **批量处理**：一次处理整个目录
5. **错误重试**：失败自动重试3次

## 获取帮助

如果遇到问题，请查看：
- `doc/FLAC_METADATA_RESEARCH.md` - 音轨号功能文档
- `doc/README.md` - 完整项目文档
- `logs/decrypt.log` - 错误日志

---

**技能创建时间**：2026-01-26
**技能版本**：1.0.0
**项目路径**：D:\WorkDev\qqmusic_decryptor
