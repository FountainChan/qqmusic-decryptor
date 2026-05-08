# Copyright (C) 2026 FountainChan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# GUI 部分基于 strelitzia-reg/qqmusic-decryptor (MIT) 修改
# https://github.com/strelitzia-reg/qqmusic-decryptor

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import frida
import os
import hashlib
import threading
import logging
import sys
from datetime import datetime
import shutil
import configparser
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from metadata_utils import (
    extract_track_number_from_filename,
    add_track_number_to_flac,
    process_album_metadata,
    QQMusicAPIClient
)

class QQMusicDecryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QQ音乐解密工具 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 新增：配置日志（使用 logging.basicConfig）
        # 获取项目根目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir.endswith(('gui_backup', 'gui')):
            # src/gui/ 下则向上两级到项目根目录
            project_root = os.path.dirname(os.path.dirname(script_dir))
        else:
            # 否则，使用脚本目录
            project_root = script_dir
        
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'gui.log')
        
        # 配置日志（输出到文件）
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 创建文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # 配置根 logger（只输出到文件）
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler],
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True
        )
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # 新增：删除选项变量（初始默认值，load_config 会更新）
        self.delete_source_var = tk.BooleanVar(value=True)
        self.delete_empty_dirs_var = tk.BooleanVar(value=True)
        self.delete_lyrics_var = tk.BooleanVar(value=True)
        self.default_delete_source = True
        self.default_delete_empty_dirs = True
        self.default_delete_lyrics = True

        # 新增：删除统计变量
        self.deleted_files = 0
        self.deleted_dirs = 0

        self.load_config()
 
        self.setup_ui()

        # 状态变量
        self.is_processing = False
        self.session = None
        self.script = None

        # 新增：删除选项变量
        self.delete_source_var = tk.BooleanVar(value=True)
        self.delete_empty_dirs_var = tk.BooleanVar(value=True)
        self.delete_lyrics_var = tk.BooleanVar(value=True)
        self.default_delete_source = True
        self.default_delete_empty_dirs = True
        self.default_delete_lyrics = True
        
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="QQ音乐解密工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入目录选择
        ttk.Label(main_frame, text="输入目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.input_path, width=50).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="浏览", command=self.browse_input).grid(row=1, column=2, pady=5)
        
        # 输出目录选择
        ttk.Label(main_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.output_path, width=50).grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="浏览", command=self.browse_output).grid(row=2, column=2, pady=5)
        
        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)

        # 选项框架
        options_frame = ttk.LabelFrame(main_frame, text="选项")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=5, pady=5)

        # 删除源文件复选框
        ttk.Checkbutton(
            options_frame,
            text="转换后删除源文件",
            variable=self.delete_source_var
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        # 删除空目录复选框
        ttk.Checkbutton(
            options_frame,
            text="删除空目录",
            variable=self.delete_empty_dirs_var
        ).grid(row=0, column=1, sticky=tk.W, pady=2, padx=10)

        # 删除歌词文件复选框
        ttk.Checkbutton(
            options_frame,
            text="同时删除歌词文件",
            variable=self.delete_lyrics_var
        ).grid(row=0, column=2, sticky=tk.W, pady=2)

        # 控制按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始解密", command=self.start_decryption)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_decryption, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="准备就绪")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # 统计信息
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=8, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(stats_frame, text="统计信息:").grid(row=0, column=0, sticky=tk.W)
        self.stats_text = tk.StringVar(value="总文件: 0, 成功: 0, 失败: 0, 跳过: 0")
        ttk.Label(stats_frame, textvariable=self.stats_text).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # 日志区域
        ttk.Label(main_frame, text="操作日志:").grid(row=9, column=0, sticky=tk.W, pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(main_frame, width=80, height=20)
        self.log_area.grid(row=10, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 署名
        ttk.Label(main_frame, text="工具由 Strelitzia 开发", font=("Arial", 8), foreground="gray").grid(
            row=9, column=2, sticky=tk.E, pady=(10, 0)
        )
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 设置默认路径（从配置文件读取）
        self.input_path.set(self.default_input_dir)
        self.output_path.set(self.default_output_dir)
        
        # 添加 TextHandler 到 logger（输出到 GUI 文本框）
        # 这样日志就会同时输出到：文件、GUI 文本框
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        self.text_handler = TextHandler(self.log_area)
        self.text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.text_handler)
    
    # setup_logging() 方法已被 logging.basicConfig() 替代
    # 日志配置现在在 __init__() 方法中完成
    # 同时输出到文件和 GUI 文本框
    
    # 原来的 setup_logging() 方法（已废弃）
    # def setup_logging(self):
    #     # 创建自定义日志处理器
    #     class TextHandler(logging.Handler):
    #         def __init__(self, text_widget):
    #             super().__init__()
    #             self.text_widget = text_widget
    #         
    #         def emit(self, record):
    #             msg = self.format(record)
    #             self.text_widget.insert(tk.END, msg + '\n')
    #             self.text_widget.see(tk.END)
    #     
    #     # 配置日志
    #     self.log_handler = TextHandler(self.log_area)
    #     self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    #     
    #     self.logger = logging.getLogger()
    #     self.logger.setLevel(logging.INFO)
    #     self.logger.addHandler(self.log_handler)
    
    def load_config(self):
        """
        加载配置文件

        从 config.ini 读取：
        1. 路径配置作为默认值（用于 GUI 默认路径）
        2. 删除选项配置作为默认值
        """
        self.config = configparser.ConfigParser()

        # 默认值（从 config.ini 的 PATHS 部分）
        default_input_dir = "G:\\QQMusic\\Download\\VipSongsDownload"
        default_output_dir = "G:\\QQMusic\\Decrypted\\VipSongsDownload"

        # 默认删除配置
        default_delete_source = True
        default_delete_empty_dirs = True
        default_delete_lyrics = True

        # 默认元数据处理模式配置
        default_metadata_processing_mode = 'batch'
        default_skip_metadata_during_decrypt = True

        # 读取配置文件
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config.ini"
        )

        if os.path.exists(config_path):
            try:
                self.config.read(config_path, encoding='utf-8')

                # 读取路径配置
                if 'PATHS' in self.config:
                    default_input_dir = self.config['PATHS'].get('input_dir', default_input_dir)
                    default_output_dir = self.config['PATHS'].get('output_dir', default_output_dir)

                # 读取删除配置
                if 'OPTIONS' in self.config:
                    default_delete_source = self.config['OPTIONS'].getboolean(
                        'delete_source', fallback=True
                    )
                    default_delete_empty_dirs = self.config['OPTIONS'].getboolean(
                        'delete_empty_dirs', fallback=True
                    )
                    default_delete_lyrics = self.config['OPTIONS'].getboolean(
                        'delete_lyrics', fallback=True
                    )

                    # 读取元数据处理模式配置
                    default_metadata_processing_mode = self.config['OPTIONS'].get(
                        'metadata_processing_mode', fallback='batch'
                    )
                    default_skip_metadata_during_decrypt = self.config['OPTIONS'].getboolean(
                        'skip_metadata_during_decrypt', fallback=True
                    )

                print(f"[配置] 已加载配置文件: {config_path}")
            except Exception as e:
                print(f"[配置] 读取配置文件失败: {e}，使用默认配置")
        else:
            print(f"[配置] 配置文件不存在: {config_path}，使用默认配置")

        # 保存为实例变量，供后续使用
        self.default_input_dir = default_input_dir
        self.default_output_dir = default_output_dir
        self.default_delete_source = default_delete_source
        self.default_delete_empty_dirs = default_delete_empty_dirs
        self.default_delete_lyrics = default_delete_lyrics
        self.metadata_processing_mode = default_metadata_processing_mode
        self.skip_metadata_during_decrypt = default_skip_metadata_during_decrypt
    
    def browse_input(self):
        path = filedialog.askdirectory(title="选择加密文件目录")
        if path:
            self.input_path.set(path)
    
    def browse_output(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_path.set(path)
    
    def log(self, message, level=logging.INFO):
        logging.getLogger().log(level, message)
    
    def clear_log(self):
        self.log_area.delete(1.0, tk.END)
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_stats(self, total, success, failed, skipped):
        self.stats_text.set(f"总文件: {total}, 成功: {success}, 失败: {failed}, 跳过: {skipped}")
    
    def start_decryption(self):
        if not self.input_path.get() or not self.output_path.get():
            messagebox.showerror("错误", "请选择输入和输出目录")
            return
        
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("错误", "输入目录不存在")
            return
        
        # 创建输出目录
        os.makedirs(self.output_path.get(), exist_ok=True)
        
        # 更新UI状态
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress['value'] = 0

        # 新增：重置删除统计
        self.deleted_files = 0
        self.deleted_dirs = 0
        
        # 在新线程中运行解密
        thread = threading.Thread(target=self.run_decryption)
        thread.daemon = True
        thread.start()
    
    def stop_decryption(self):
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("解密已停止")

        # 断开Frida连接
        if self.session:
            try:
                self.session.detach()
            except:
                pass

    def copy_lyrics_file(self, input_file, output_file):
        """
        复制同名的歌词文件到输出目录

        Args:
            input_file: 输入音频文件的完整路径
            output_file: 输出音频文件的完整路径
        """
        input_lyric = os.path.splitext(input_file)[0] + ".lrc"
        output_lyric = os.path.splitext(output_file)[0] + ".lrc"

        if not os.path.exists(input_lyric):
            return

        try:
            os.makedirs(os.path.dirname(output_lyric), exist_ok=True)
            shutil.copy2(input_lyric, output_lyric)
        except Exception as e:
            pass

    def delete_source_file(self, input_file, delete_lyrics=False):
        """
        删除源文件和（可选的）歌词文件

        注意：
        - 只检查源文件是否存在，不验证歌词复制是否成功（简化方案）
        - copy_lyrics_file() 方法无需修改

        Args:
            input_file: 输入文件的完整路径
            delete_lyrics: 是否同时删除歌词文件

        Returns:
            int: 删除的文件数量
        """
        deleted_count = 0

        try:
            # 删除源音频文件（解密成功后文件一定存在）
            if os.path.exists(input_file):
                os.remove(input_file)
                deleted_count += 1
                self.log(f"✓ 已删除源文件: {os.path.basename(input_file)}")

            # 删除歌词文件（只在源文件存在时检查）
            if delete_lyrics:
                lyric_file = os.path.splitext(input_file)[0] + ".lrc"
                if os.path.exists(lyric_file):
                    os.remove(lyric_file)
                    deleted_count += 1
                    self.log(f"✓ 已删除歌词文件: {os.path.basename(lyric_file)}")

        except Exception as e:
            self.log(f"删除文件失败: {e}", logging.WARNING)

        return deleted_count

    def cleanup_empty_dirs(self, dir_path, root_dir):
        """
        递归删除空目录，直到 root_dir

        Args:
            dir_path: 要检查的目录路径
            root_dir: 根目录（停止删除的边界）

        Returns:
            int: 删除的目录数量
        """
        deleted_count = 0

        # 规范化路径
        dir_path = os.path.normpath(dir_path)
        root_dir = os.path.normpath(root_dir)

        # 如果已经到达根目录或超出范围，停止
        if dir_path == root_dir or not dir_path.startswith(root_dir):
            return deleted_count

        try:
            # 检查目录是否为空
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                deleted_count += 1
                self.log(f"✓ 已删除空目录: {dir_path}")

                # 递归删除父目录
                parent_dir = os.path.dirname(dir_path)
                deleted_count += self.cleanup_empty_dirs(parent_dir, root_dir)

        except Exception as e:
            self.log(f"删除目录失败: {e}", logging.WARNING)

        return deleted_count

    def add_flac_metadata(self, flac_file_path):
        """
        为 FLAC 文件添加元数据（音轨号、封面、发行年份）
        
        Args:
            flac_file_path (str): FLAC 文件路径
        """
        try:
            filename = os.path.basename(flac_file_path)
            
            # 步骤1：添加音轨号
            track_number = extract_track_number_from_filename(filename)
            
            if track_number is not None:
                success = add_track_number_to_flac(flac_file_path, track_number)
                if success:
                    self.log(f"✓ 已添加音轨号 {track_number}")
                else:
                    self.log(f"✗ 添加音轨号失败", logging.WARNING)
            
            # 步骤2：处理专辑元数据（封面、发行年份）
            self.log("获取专辑信息...")
            api_client = QQMusicAPIClient()
            result = process_album_metadata(flac_file_path, api_client, use_cache=True)
            
            if result['success']:
                metadata = result.get('metadata', {})
                if metadata:
                    pub_year = metadata.get('pub_year')
                    if pub_year:
                        self.log(f"✓ 已添加发行年份 {pub_year}")
                        
                    if metadata.get('cover_data'):
                        self.log("✓ 已嵌入封面到文件")
                        self.log("✓ 已保存封面到 cover.jpg")
            else:
                self.log(f"未找到专辑信息: {result['message']}", logging.WARNING)
        
        except Exception as e:
            self.log(f"添加元数据异常: {e}", logging.WARNING)

    def run_supplement_metadata(self, album_dir):
        """
        运行元数据补充脚本

        处理整个输出目录，批量添加音轨号、封面、年份
        """
        import subprocess

        try:
            # 检查 supplement_album_metadata.py 是否存在
            script_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'supplement_album_metadata.py'
            )

            if not os.path.exists(script_path):
                self.log(f"元数据脚本不存在: {script_path}", logging.WARNING)
                return

            # 构建命令
            cmd = ['python', script_path, album_dir]

            self.log(f"执行命令: {' '.join(cmd)}")

            # 运行脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            # 输出脚本输出
            stdout = result.stdout or ''
            for line in stdout.split('\n'):
                if line.strip() and ('INFO' in line or '处理' in line):
                    self.log(line.strip())

            # 输出错误信息
            stderr = result.stderr or ''
            for line in stderr.split('\n'):
                if line.strip():
                    self.log(line.strip(), logging.ERROR)

            if result.returncode == 0:
                self.log("元数据处理成功")
            else:
                self.log(f"元数据处理失败，错误代码: {result.returncode}", logging.ERROR)

        except Exception as e:
            self.log(f"执行元数据脚本异常: {e}", logging.ERROR)

    def run_decryption(self):
        try:
            input_dir = self.input_path.get()
            output_dir = self.output_path.get()
            
            self.log("正在连接到QQ音乐进程...")
            self.update_status("正在连接到QQ音乐...")
            
            # 连接到QQ音乐进程
            try:
                self.session = frida.attach("QQMusic.exe")
                self.log("✓ 成功连接到QQ音乐进程")
            except Exception as e:
                self.log(f"✗ 连接QQ音乐进程失败: {e}", logging.ERROR)
                self.log("请确保: 1) QQ音乐正在运行 2) frida-server已启动", logging.ERROR)
                self.stop_decryption()
                return
            
            # 加载解密脚本
            try:
                hook_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hook_qq_music.js")
                with open(hook_path, "r", encoding="utf-8") as f:
                    script_code = f.read()
                self.script = self.session.create_script(script_code)
                self.script.load()
                self.log("✓ 解密脚本加载成功")
            except Exception as e:
                self.log(f"✗ 加载解密脚本失败: {e}", logging.ERROR)
                self.stop_decryption()
                return
            
            # 查找加密文件
            self.log("正在扫描加密文件...")
            self.update_status("正在扫描文件...")
            
            encrypted_files = []
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    file_ext = os.path.splitext(file)[-1].lower()
                    if file_ext in [".mflac", ".mgg"]:
                        encrypted_files.append(os.path.join(root, file))
            
            if not encrypted_files:
                self.log("未找到任何.mflac或.mgg文件", logging.WARNING)
                self.stop_decryption()
                return
            
            self.log(f"找到 {len(encrypted_files)} 个加密文件")
            self.update_status(f"开始解密 {len(encrypted_files)} 个文件...")
            
            # 统计变量
            total_files = len(encrypted_files)
            success_files = 0
            failed_files = 0
            skipped_files = 0
            
            # 处理每个文件
            for i, encrypted_file in enumerate(encrypted_files):
                if not self.is_processing:
                    break
                
                # 更新进度
                progress = (i / total_files) * 100
                self.progress['value'] = progress
                self.update_stats(total_files, success_files, failed_files, skipped_files)
                
                # 获取相对路径以保留目录结构
                relative_path = os.path.relpath(encrypted_file, input_dir)
                file_name = os.path.basename(encrypted_file)
                self.log(f"处理文件 {i+1}/{total_files}: {file_name}")
                
                # 构建输出文件名
                file_ext = os.path.splitext(file_name)[-1].lower()
                if file_ext == ".mflac":
                    output_ext = ".flac"
                else:  # .mgg
                    output_ext = ".ogg"
                
                output_file = os.path.splitext(file_name)[0] + output_ext
                # 替换扩展名并保留目录结构
                relative_path = os.path.splitext(relative_path)[0] + output_ext
                output_file_path = os.path.join(output_dir, relative_path)
                
                # 创建输出目录（包含子目录）
                output_dir_with_path = os.path.dirname(output_file_path)
                os.makedirs(output_dir_with_path, exist_ok=True)
                
                
                # 检查文件是否已存在
                if os.path.exists(output_file_path):
                    self.log(f"文件已存在，跳过: {output_file}")
                    skipped_files += 1
                    continue
                
                # 创建临时文件名
                temp_file_name = hashlib.md5(encrypted_file.encode()).hexdigest() + output_ext
                temp_file_path = os.path.join(output_dir, temp_file_name)
                
                try:
                    # 调用解密函数
                    self.log(f"开始解密: {file_name}")
                    result = self.script.exports_sync.decrypt(encrypted_file, temp_file_path)
                    
                    if "Success" in result:
                        # 重命名临时文件
                        os.rename(temp_file_path, output_file_path)
                        success_files += 1
                        self.log(f"✓ 解密成功: {output_file}")

                        # 跳过解密时的元数据修改
                        # 元数据将在所有文件解密完成后统一处理
                        if not self.skip_metadata_during_decrypt and output_file_path.lower().endswith('.flac'):
                            self.add_flac_metadata(output_file_path)

                        self.copy_lyrics_file(encrypted_file, output_file_path)

                        # === 新增：删除源文件和空目录 ===
                        if self.delete_source_var.get():
                            # 删除源文件和歌词文件
                            deleted_count = self.delete_source_file(
                                encrypted_file,
                                self.delete_lyrics_var.get()
                            )
                            self.deleted_files += deleted_count

                            # 删除空目录
                            if self.delete_empty_dirs_var.get():
                                file_dir = os.path.dirname(encrypted_file)
                                deleted_dirs = self.cleanup_empty_dirs(file_dir, input_dir)
                                self.deleted_dirs += deleted_dirs
                        # ===============================
                    else:
                        failed_files += 1
                        self.log(f"✗ 解密失败: {file_name} - {result}", logging.ERROR)
                        # 清理临时文件
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                            
                except Exception as e:
                    failed_files += 1
                    self.log(f"✗ 处理文件时出错: {file_name} - {e}", logging.ERROR)
                    # 清理临时文件
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
            
            # 完成处理
            self.progress['value'] = 100
            self.update_stats(total_files, success_files, failed_files, skipped_files)
            if self.is_processing:
                self.log("=" * 50)
                self.log("批量解密完成!")
                self.log(f"总文件数: {total_files}")
                self.log(f"成功: {success_files}")
                self.log(f"失败: {failed_files}")
                self.log(f"跳过: {skipped_files}")
                self.log(f"已删除文件: {self.deleted_files}")
                self.log(f"已删除目录: {self.deleted_dirs}")
                self.log(f"输出目录: {output_dir}")

                # 解密完成后统一处理元数据（批量模式）
                if self.metadata_processing_mode == 'batch':
                    self.log("=" * 50)
                    self.log("解密完成，开始统一处理元数据")
                    self.log("=" * 50)
                    self.update_status("正在补充元数据...")

                    # 调用批量元数据处理
                    self.run_supplement_metadata(output_dir)

                    self.log("=" * 50)
                    self.log("元数据处理完成")
                    self.log("=" * 50)

                self.update_status("解密完成")

                if failed_files == 0:
                    messagebox.showinfo("完成", 
                        f"解密完成！成功处理 {success_files} 个文件。\n"
                        f"已删除文件: {self.deleted_files}\n"
                        f"已删除目录: {self.deleted_dirs}")
                else:
                    messagebox.showwarning("完成", 
                        f"解密完成！\n"
                        f"成功: {success_files}\n"
                        f"失败: {failed_files}\n"
                        f"跳过: {skipped_files}\n"
                        f"已删除文件: {self.deleted_files}\n"
                        f"已删除目录: {self.deleted_dirs}")
            
        except Exception as e:
            self.log(f"解密过程发生错误: {e}", logging.ERROR)
            messagebox.showerror("错误", f"解密过程发生错误: {e}")
        
        finally:
            # 断开连接
            if self.session:
                try:
                    self.session.detach()
                except:
                    pass
            
            # 恢复UI状态
            self.is_processing = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    # 检查frida是否可用
    try:
        import frida
    except ImportError:
        print("错误: 未安装frida，请先运行: pip install -r requirements.txt")
        input("按回车键退出...")
        sys.exit(1)
    
    root = tk.Tk()
    app = QQMusicDecryptorGUI(root)
    root.mainloop()