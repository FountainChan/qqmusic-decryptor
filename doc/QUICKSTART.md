# 快速开始指南

## 🚀 5分钟快速上手

### 第一步：安装依赖（1分钟）

双击运行 `install_dependencies.bat`

等待安装完成，然后点击任意键关闭。

### 第二步：下载frida-server（2分钟）

1. 访问：https://github.com/frida/frida/releases
2. 下载文件：`frida-server-16.7.10-windows-x86_64.exe.xz`
3. 解压文件（使用WinRAR或7-Zip）
4. 将解压后的 `frida-server.exe` 复制到项目目录 `D:\WorkDev\qqmusic_decryptor\`
5. 确认文件在目录中

### 第三步：启动服务（1分钟）

1. 右键点击 `start_frida_server.bat`
2. 选择"以管理员身份运行"
3. **重要**：不要关闭此窗口！保持打开状态

### 第四步：启动QQ Music（30秒）

- 启动QQ Music客户端
- 确保已登录VIP账号
- 最小化到系统托盘

### 第五步：开始解密（1分钟）

双击运行 `auto_decrypt.bat`

等待转换完成，查看结果统计。

---

## 📋 日常使用

### 每次使用前（1分钟）

1. 确认frida-server窗口是否打开
2. 确认QQ Music是否运行
3. 双击运行 `auto_decrypt.bat`

### 遇到问题？

运行 `check_env.bat` 检查环境

查看 `logs\decrypt.log` 了解详细错误

---

## ⚠️ 重要提示

### 必须保持运行

- frida-server窗口必须保持打开
- QQ Music必须保持运行
- 不要在解密过程中关闭任何窗口

### 首次转换

- 30个文件大约需要15-20分钟
- 后续转换新文件会更快（跳过已存在的）
- 确保磁盘有足够空间（约1.2GB）

### 文件位置

- **输入**：`G:\QQMusic\Download`
- **输出**：`G:\QQMusic\Decrypted`
- **日志**：`D:\WorkDev\qqmusic_decryptor\logs\decrypt.log`

---

## 🆘 快速故障排除

### 问题：双击bat文件没有反应
**解决**：可能是Python路径问题，右键 → 编辑，确认python命令路径正确

### 问题：提示"需要管理员权限"
**解决**：右键 `start_frida_server.bat` → 以管理员身份运行

### 问题：QQ Music启动失败
**解决**：手动启动QQ Music，确认能正常运行

### 问题：转换速度很慢
**解决**：这是正常的，每个文件约30-40秒，请耐心等待

### 问题：部分文件转换失败
**解决**：
1. 查看日志文件
2. 在QQ Music中重新下载失败的文件
3. 再次运行 `auto_decrypt.bat`

---

## 📊 预期结果

### 成功标志

```
============================================================
  🎉 解密任务完成！
============================================================
  总文件数: 30
  成功: 30 ✅
  失败: 0 ❌
  跳过: 0 ⏭️
  处理时间: 15分23秒
  平均速度: 1.95 文件/分钟
============================================================
```

### 检查转换结果

打开 `G:\QQMusic\Decrypted` 目录：
- 应该能看到转换后的 `.flac` 文件
- 目录结构与原始结构一致
- 文件可以正常播放

---

## 🔄 下次使用更简单

### 自动化启动脚本（可选）

创建一个 `一键启动.bat` 文件：

```batch
@echo off
start "" "D:\WorkDev\qqmusic_decryptor\start_frida_server.bat"
timeout /t 5
start "" "D:\Software\Tencent\QQMusic\QQMusic1951.01.07.35\QQMusic.exe"
timeout /t 10
call "D:\WorkDev\qqmusic_decryptor\auto_decrypt.bat"
```

这样只需要双击一个文件即可完成所有步骤！

---

## 💡 使用技巧

### 1. 后台运行

- 将frida-server最小化
- 将QQ Music最小化到系统托盘
- auto_decrypt.bat运行时会显示详细进度

### 2. 日志查看

转换过程中可以实时查看日志：
```bash
type logs\decrypt.log
```

### 3. 统计信息

每次转换后会生成 `logs\stats.json`，包含详细的统计信息。

### 4. 增量更新

下载新音乐后，再次运行 `auto_decrypt.bat`，工具会自动跳过已转换的文件，只转换新的文件。

---

## 📞 需要帮助？

如果以上方法都无法解决问题：

1. 查看 `README.md` 获取完整文档
2. 查看 `logs\decrypt.log` 获取详细错误信息
3. 尝试使用GUI版本作为备选方案

---

**祝您使用愉快！** 🎵
