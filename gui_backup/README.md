# QQ音乐解密工具 🎵

[![GitHub 最新版本](https://img.shields.io/github/v/release/Strelitzia/qqmusic-decryptor)](https://github.com/Strelitzia/qqmusic-decryptor/releases)
[![许可证: MIT](https://img.shields.io/badge/许可证-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 版本](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![欢迎提交PR](https://img.shields.io/badge/PRs-欢迎-brightgreen.svg)](CONTRIBUTING.md)

一款用于批量解密QQ音乐VIP下载歌曲（`.mflac`、`.mgg`格式）的强大、易用的桌面工具。基于Python和Frida开发，拥有简洁的图形界面和稳定的解密能力。

## ✨ 功能特点

*   **图形用户界面 (GUI)**：使用Tkinter构建的直观界面，无需命令行操作经验。
*   **批量处理**：自动解密选定目录下的所有`.mflac`和`.mgg`文件。
*   **实时进度**：通过进度条、详细日志和文件统计信息实时监控解密过程。
*   **智能文件管理**：自动跳过已解密的文件，节省时间。
*   **安全可靠**：采用分块读取和重试机制，确保大文件解密的稳定性。
*   **跨格式支持**：将`.mflac`无缝转换为`.flac`，将`.mgg`无缝转换为`.ogg`。

## 📸 界面截图

![QQ音乐解密工具图形界面](screenshot.png)

## 🚀 快速开始

### 先决条件

在使用本工具前，请确保你的系统已满足以下条件：

1.  **Python 3.8 或更高版本**：[下载 Python](https://www.python.org/downloads/)
2.  **QQ音乐客户端**：最新版本，并已使用VIP账号登录（用于下载歌曲）。
3.  **管理员权限**（在Windows上运行`frida-server`所必需）。

### 安装与配置

1.  **克隆本仓库**
    ```bash
    git clone https://github.com/Strelitzia/qqmusic-decryptor.git
    cd qqmusic-decryptor
    ```

2.  **安装Python依赖**
    工具的核心依赖列在 `requirements.txt` 中。
    ```bash
    pip install -r requirements.txt
    ```
    > **重要的兼容性说明**：指定的 `frida==16.7.10` 要求 **Python 3.8 或更高版本**。如果你正在使用Python 3.6或3.7，请升级你的Python解释器。

3.  **启动 Frida-Server（关键步骤）**
    *   从 [Frida 官方发布页](https://github.com/frida/frida/releases) 下载 **版本匹配** 的 `frida-server`（需与Python包`frida`的版本`16.7.10`一致，例如查找 `frida-server-16.7.10-windows-x86_64.exe.xz`)。
    *   解压得到 `.exe` 文件，并**以管理员身份**在命令提示符窗口中运行它。**在使用解密工具期间，请保持此窗口开启**。
    ```bash
    # 示例：进入你的下载目录并运行
    frida-server.exe
    ```

### 使用方法

1.  **启动QQ音乐**：确保官方的QQ音乐客户端正在后台运行。
2.  **运行解密工具**：
    ```bash
    python main_gui.py
    ```
    或者在Windows上直接双击 `run.bat` 文件。
3.  **使用图形界面**：
    *   **输入目录**：点击“浏览”选择包含你的`.mflac`/`.mgg`文件的文件夹（例如 `D:\Music\VipSongsDownload`）。
    *   **输出目录**：选择一个文件夹用于保存解密后的文件（例如 `D:\DecryptedMusic`）。
    *   **开始**：点击“开始解密”按钮。进度条和日志窗口将显示实时状态。
    *   **停止**：你可以随时使用“停止”按钮暂停处理过程。

## 📖 常见问题解答 (FAQ)

<details>
<summary><b>解密失败或工具卡住无响应。</b></summary>

*   **验证Frida连接**：打开一个新的终端，运行 `frida-ps`。如果它能列出进程（包括`QQMusic.exe`），则连接正常。
*   **检查版本**：确保 `frida` Python包（`16.7.10`）和 `frida-server` 可执行文件的版本**完全一致**。
*   **重启服务**：关闭并重新启动QQ音乐和`frida-server`（以管理员身份），然后重试。
</details>

<details>
<summary><b>输出的文件损坏或无法播放。</b></summary>

*   这通常表明解密过程中读取不完整。
*   请确保没有其他重型应用程序占用过多的内存/CPU资源。
*   尝试在QQ音乐中重新下载该特定歌曲，然后再次解密。
</details>

<details>
<summary><b>出现“ModuleNotFoundError: No module named 'frida'”错误。</b></summary>

*   依赖项未正确安装。请运行：
    ```bash
    pip install -r requirements.txt
    ```
    并确保你的Python版本为3.8或更高。
</details>

<details>
<summary><b>安装`frida`时出现版本错误。</b></summary>

*   本项目要求 `frida==16.7.10`，该版本依赖于 **Python 3.8+**。
*   请从[官方网站](https://www.python.org/downloads/)将你的Python解释器升级到3.8或更高版本。
</details>

## 🤝 贡献指南

我们欢迎任何形式的贡献！欢迎提交 Pull Request。

1.  Fork 本仓库。
2.  创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交你的更改 (`git commit -m '添加了某个神奇的功能'`)。
4.  推送到分支 (`git push origin feature/AmazingFeature`)。
5.  开启一个 Pull Request。

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细的贡献指南和工作流程。

## ⚖️ 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## ⚠️ 免责声明

本工具**仅用于教育与研究目的**。旨在让用户能够行使对其**通过QQ音乐VIP服务合法购买**的歌曲的合理使用权。

*   用户须自行负责确保其遵守当地版权法律及QQ音乐的服务条款。
*   开发者**不对**任何滥用本软件的行为负责。
*   请通过官方渠道支持艺术家，购买正版音乐。

---

**工具由 Strelitzia 开发与维护**