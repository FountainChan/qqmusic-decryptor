# 🧠 Project Anatomy — qqmusic_decryptor

> Frida-based QQ Music批量解密工具。将 .mflac/.mgg 转为 .flac/.ogg，支持 CLI/GUI 双模式、目录结构保留、元数据补充。

---

## ./

入口脚本与配置文件位于项目根目录。

### Shell 入口 (Git Bash)
- `run_supplement.sh` -- 专辑元数据补充入口，调用 `src/supplement_album_metadata.py` (~1000 tok)
- `run_gui_simple.sh` -- GUI解密启动（前台，显示控制台日志）(~250 tok)
- `start_gui.sh` -- start_gui.sh (~0 tok)
- `start_frida_server.sh` -- 启动 frida-server 前置服务，调用 `three-party/frida-server.exe` (~400 tok)
- `auto_decrypt.sh` -- CLI自动化解密入口，调用 `src/main_cli.py` (~400 tok)
- `check_env.sh` -- check_env.sh (~0 tok)

### Batch 入口 (Windows)
- `run_supplement.bat` -- run_supplement 的 Batch 版本 (~1100 tok)
- `run_gui_simple.bat` -- run_gui_simple 的 Batch 版本 (~80 tok)
- `start_gui_english.bat` -- start_gui_english.bat (~0 tok)
- `start_frida_server.bat` -- start_frida_server 的 Batch 版本 (~500 tok)
- `auto_decrypt.bat` -- auto_decrypt 的 Batch 版本 (~400 tok)
- `check_env.bat` -- check_env.bat (~0 tok)
- `install_dependencies.bat` -- install_dependencies.bat (~0 tok)

### 配置文件
- `config.ini` -- 输入/输出目录、日志级别、重试参数等配置 (~200 tok)
- `requirements.txt` -- Python依赖: frida==16.7.10 (~20 tok)
- `.gitignore` -- 忽略规则: __pycache__/ logs/ *.bak drops/ 等 (~80 tok)

### 项目文档
- `AGENTS.md` -- AI助手项目文档，含架构/用法/最佳实践 (~20000 tok)
- `manual_fix_guide.txt` -- 手动修复操作说明 (~400 tok)

---

## src/
核心源码目录，包含 Python 和 JavaScript 源码。

### Python 核心
- `main_cli.py` -- CLI解密主程序，Frida连接/批量解密/统计 (~12000 tok)
- `supplement_album_metadata.py` -- 专辑元数据补充脚本，封面嵌入+发行年份获取 (~10200 tok)
- `metadata_utils.py` -- 元数据工具库，音轨号提取/FLAC写入/API客户端包装 (~6400 tok)
- `qqmusic_api_client.py` -- QQ Music API客户端，专辑信息查询/封面下载 (~6100 tok)

### Hook 脚本
- `hook_qq_music.js` -- Frida Hook脚本，Hook QQMusicCommon.dll 解密函数 (~1400 tok)

### src/gui/ (GUI 独立版本)
- `main_gui.py` -- tkinter GUI主程序，Frida解密/进度显示/配置管理 (~11600 tok)
- `hook_qq_music.js` -- GUI版独立 Frida Hook 脚本 (~1400 tok)
- `README.md` -- GUI版说明文档 (~2600 tok)
- `LICENSE` -- MIT 许可证
- `.gitignore` -- GUI目录 git 忽略规则
- `requirements.txt` -- GUI版依赖声明（空文件）
- `tester.txt` -- 空占位文件

---

## three-party/
第三方二进制文件。

- `frida-server.exe` -- Frida服务端二进制，供 `start_frida_server.sh/bat` 调用 (~69MB)

---

## doc/
文档目录，按分类归档的子目录。

- `index.md` -- 文档导航总入口 (~2300 tok)
- `guide/` (7篇) -- 用户手册/快速开始/GUI指南/Shell指南/API文档
- `overview/` (8篇) -- 项目总结/状态报告/技能说明/Claude集成/问题记录
- `feature/` (9篇) -- 封面元数据/音轨号/歌词复制/源文件删除等功能文档
- `fix/` (22篇) -- 元数据处理/封面保存/OGG支持/GUI日志/Hook修复等方案和报告
- `ops/` (9篇) -- BAT清理/换行符修复/备份管理/文档整理/脚本创建报告

---

## docs/
规划与需求文档。

- `brainstorms/` -- 头脑风暴需求文档
- `plans/` -- 实施计划

---

## .skills/
OpenCode 技能定义。

- `qqmusic_decryptor.md` -- Skill 描述文档，含触发词/工作流 (~2400 tok)
- `qqmusic_decryptor.json` -- Skill 元数据配置，含依赖检查/操作步骤 (~1000 tok)

---

## openspec/
OpenSpec 变更提案系统。

- `AGENTS.md` -- OpenSpec 指令集，用于提案创建和应用规范 (~10000 tok)

---

## .vscode/
- `extensions.json` -- 推荐安装 OpenCode 扩展 (~40 tok)

---

## logs/
- `gui.log` -- GUI运行时日志

## .wolf/

- `.wolf\anatomy.md` -- > Frida-based QQ Music批量解密工具。将 .mflac/.mgg 转为 .flac/.ogg，支持 CLI/GUI 双模式、目录结构保留、元数据补充。 (~734 tok)

## src\gui/

- `src\gui\main_gui.py` -- main_gui.py (~0 tok)
