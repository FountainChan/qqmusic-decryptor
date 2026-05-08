# GUI 启动说明

## 启动GUI的方法

### 方法1: 双击启动（推荐）

在文件管理器中双击以下任一脚本：

1. **quick_start_gui.bat** - 快速启动（推荐）
   - 使用 pythonw 启动GUI，在新窗口中打开
   - 不会阻塞命令行
   - 更简洁的启动方式

2. **launch_gui.bat** - 标准启动
   - 完整的环境检查
   - 详细的使用说明
   - 适合首次使用

### 方法2: 命令行启动

打开命令提示符（cmd），执行：

```batch
cd D:\WorkDev\qqmusic_decryptor
quick_start_gui.bat
```

或者：

```batch
cd D:\WorkDev\qqmusic_decryptor
pythonw gui_backup\main_gui.py
```

### 方法3: 右键启动

右键点击 `quick_start_gui.bat`，选择"以管理员身份运行"

---

## 启动前检查

在启动GUI之前，请确保：

1. **frida-server 正在运行**
   - 右键 `start_frida_server.bat` → 以管理员身份运行
   - 保持窗口打开状态

2. **QQ Music 正在运行**
   - 启动QQ Music客户端
   - 确保已登录VIP账号

3. **Python和Frida已安装**
   - Python 3.8+
   - Frida 16.7.10

---

## 默认配置

GUI 启动后，默认配置为：

- **输入目录**: `G:\QQMusic\Download\VipSongsDownload`
- **输出目录**: `G:\QQMusic\Decrypted\VipSongsDownload`

如果需要修改，可以点击相应的按钮选择其他目录。

---

## 使用步骤

1. 启动GUI程序
2. 检查输入/输出目录是否正确
3. 点击"开始解密"按钮
4. 等待转换完成
5. 查看转换结果

---

## 预期结果

输入示例：
```
G:\QQMusic\Download\VipSongsDownload\歌手\专辑\歌曲.mflac
```

输出示例：
```
G:\QQMusic\Decrypted\VipSongsDownload\歌手\专辑\歌曲.flac
```

特性：
- ✅ 完全保留原始目录结构
- ✅ 子目录自动创建
- ✅ 文件扩展名正确转换（`.mflac` → `.flac`, `.mgg` → `.ogg`）

---

## 注意事项

1. **GUI窗口启动后**
   - 不要关闭启动GUI的命令行窗口（如果有的话）
   - GUI窗口独立运行，可以在任务栏中找到

2. **转换过程中**
   - 不要关闭QQ Music客户端
   - 不要关闭frida-server窗口
   - 不要中断网络连接

3. **转换完成后**
   - 查看日志窗口中的转换结果
   - 检查输出目录中的文件
   - 可以关闭GUI窗口

---

## 故障排除

### GUI 窗口没有打开

1. 检查frida-server是否运行
2. 检查QQ Music是否运行
3. 检查Python是否正确安装
4. 查看命令行窗口中的错误信息

### 转换失败

1. 确保QQ Music已登录VIP账号
2. 检查输入目录中的文件是否有效
3. 查看GUI日志窗口中的错误信息
4. 尝试重新启动frida-server和QQ Music

### 目录结构没有保留

1. 确认使用的是修复后的版本
2. 检查 `gui_backup/main_gui.py` 第245-264行
3. 运行测试脚本验证：`python test_gui_functions.py`

---

## 快速测试

运行以下命令测试配置：

```batch
python test_gui_config.py
```

运行以下命令测试功能：

```batch
python test_gui_functions.py
```

---

## 获取帮助

如果遇到问题：

1. 查看 `TEST_REPORT.md` - 详细测试报告
2. 查看 `agents.md` - 项目完整文档
3. 查看 `claude.md` - AI助手使用指南

---

**最后更新**: 2026-01-26
**版本**: v1.1 (已修复)
