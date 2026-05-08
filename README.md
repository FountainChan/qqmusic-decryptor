
    <p align="center">
      <img src="https://img.shields.io/github/v/release/FountainChan/qqmusic-decryptor" alt="GitHub release">
      <img src="https://img.shields.io/badge/license-AGPLv3-blue" alt="License">
      <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
      <img src="https://img.shields.io/badge/frida-16.7.10-green" alt="Frida">
      <img src="https://img.shields.io/badge/PRs-welcome-brightgreen" alt="PRs Welcome">
    </p>

# 🎵 QQ Music Decryptor

> 🎯 Batch decrypt QQ Music encrypted audio files (`.mflac`/`.mgg`) to standard formats (`.flac`/`.ogg`), then supplement album metadata — all in one automated workflow.

**[📖 中文文档](README.zh-CN.md)**

---

## ✨ Features

- 🔓 **Decrypt** — Convert `.mflac` → `.flac`, `.mgg` → `.ogg` via Frida dynamic instrumentation
- 🖼️ **Album Metadata** — Embed album cover + fetch release year from QQ Music API
- 📂 **Structure Preserved** — Keep original directory hierarchy intact
- ⏭️ **Smart Skip** — Auto-skip already converted files
- 🔄 **Retry on Error** — Configurable automatic retry (default 3 attempts)
- 📋 **Detailed Logging** — Per-file decrypt log + JSON stats summary
- 🖥️ **Dual Interface** — CLI and GUI modes, pick your style

---

## 🚀 Quick Start

### 📋 Prerequisites

- ✅ **Python 3.8+**
- ✅ **QQ Music** client installed & logged in with a VIP account
- ✅ Windows (the tool hooks into `QQMusic.exe` via Frida)

### 📦 Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/qqmusic-decryptor.git
cd qqmusic-decryptor

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. (Optional) Register global commands for convenience
pip install -e .
```

After installation, use `qqmusic-decrypt`, `qqmusic-meta`, and `qqmusic-gui` from anywhere. 🎉

---

## 📖 Usage

### ⚡ Quick Commands (after `pip install -e .`)

| Command | What it does |
|---------|-------------|
| `qqmusic-decrypt` | 🔓 Decrypt all files, then supplement metadata |
| `qqmusic-meta` | 🖼️ Supplement album metadata only (cover + year) |
| `qqmusic-gui` | 🖥️ Launch the GUI application |

### 🐚 Shell Scripts (Git Bash)

```bash
# Decrypt + supplement (full workflow)
bash src/shell/auto_decrypt.sh

# Decrypt only (GUI mode, foreground)
bash src/shell/run_gui_simple.sh

# Decrypt only (GUI mode, background)
bash src/shell/start_gui.sh

# Supplement album metadata only
bash src/shell/run_supplement.sh

# Check environment
bash src/shell/check_env.sh
```

### 🪟 Batch Scripts (Windows CMD)

Double-click or run in Command Prompt:

| Script | Action |
|--------|--------|
| `src/bat/run_gui_simple.bat` | 🖥️ Launch GUI (foreground) |
| `src/bat/start_gui_english.bat` | 🖥️ Launch GUI (English, with pre-checks) |
| `src/bat/run_supplement.bat` | 🖼️ Supplement album metadata |
| `src/bat/auto_decrypt.bat` | 🔓 Full decrypt workflow |
| `src/bat/check_env.bat` | 🔍 Environment check |
| `src/bat/install_dependencies.bat` | 📦 One-click dependency install |

### ⌨️ Command-Line Details

```bash
# Decrypt with custom paths
python src/main_cli.py --input "D:\Music" --output "D:\Output"

# Supplement metadata for a specific album directory
python src/supplement_album_metadata.py "D:\Music\Decrypted\AlbumName"

# Dry-run supplement (no actual changes)
python src/supplement_album_metadata.py "D:\Music\Decrypted" --dry-run

# Verbose logging
python src/main_cli.py --verbose
```

---

## ⚙️ Configuration

Edit `config.ini` in the project root:

```ini
[PATHS]
input_dir = G:\QQMusic\Download\VipSongsDownload
output_dir = G:\QQMusic\Decrypted

[OPTIONS]
max_retries = 3
preserve_structure = true
skip_existing = true
delete_source = true
```

For supplement commands, pass the target directory directly:

```bash
qqmusic-meta "D:/MyMusic/Decrypted"
```

---

## 📁 Project Structure

```
qqmusic-decryptor/
├── src/                        # 📂 Source code
│   ├── main_cli.py             # ⚙️ CLI decrypt engine
│   ├── supplement_album_metadata.py  # 🖼️ Album metadata tool
│   ├── metadata_utils.py       # 🛠️ Metadata utilities
│   ├── qqmusic_api_client.py   # 🌐 QQ Music API client
│   ├── hook_qq_music.js        # 🪝 Frida hook script
│   ├── qqmusic_decrypt/        # 🔗 Global CLI entry points
│   │   └── cli.py              # qqmusic-decrypt / -meta / -gui
│   ├── gui/                    # 🖥️ GUI application
│   │   └── main_gui.py
│   ├── bat/                    # 🪟 Batch scripts (.bat)
│   └── shell/                  # 🐚 Shell scripts (.sh)
├── docs/                       # 📚 Documentation (user guides, dev docs, changelogs)
├── config.ini                  # ⚙️ User configuration
├── pyproject.toml              # 📦 Package config (global commands)
├── requirements.txt            # 📄 Python dependencies
├── AGENTS.md                   # 🤖 AI assistant project guide
├── README.md                   # 🇺🇸 English documentation
└── README.zh-CN.md             # 🇨🇳 中文文档
```

---

## 🧩 How It Works

1. 🪝 **Frida** attaches to the QQ Music process (`QQMusic.exe`)
2. 🎯 Hooks the `EncAndDesMediaFile` class in `QQMusicCommon.dll`
3. 📖 Reads decrypted audio data in 64KB chunks
4. 💾 Writes to a temp file, then renames to final format
5. 🖼️ Optionally supplements metadata (cover art, release year) via QQ Music API

> 💡 No separate `frida-server.exe` needed — Frida's Python package includes a built-in local helper.

---

## ❓ FAQ

**💬 Do I need to download frida-server separately?**  
No. Frida Python package includes its own built-in helper process.

**💬 Does it work without a VIP account?**  
No. The decryption relies on QQ Music's internal decrypt function, which requires a valid VIP session.

**💬 Why use Frida instead of direct file parsing?**  
QQ Music's encrypted files use a proprietary format that can only be decrypted by the QQ Music process itself. Frida allows us to call the native decrypt function in real-time.

**💬 Can I run this on Linux/macOS?**  
The tool is designed for Windows, as it hooks into `QQMusic.exe`. The CLI and metadata tools may work on other platforms if you have access to the QQ Music process.

---

## 📜 License

[GNU AGPL v3](LICENSE) © 2026 — Free to use, modify, and share. Open source forever. 🎵

---

## 🙏 Credits

- [Frida](https://frida.re/) — Dynamic instrumentation toolkit
- [mutagen](https://mutagen.readthedocs.io/) — Audio metadata handling
- [strelitzia-reg/qqmusic-decryptor](https://github.com/strelitzia-reg/qqmusic-decryptor) — The original project that inspired this tool. The GUI (`src/gui/`) is modified from this project. Big thanks! 🙌
