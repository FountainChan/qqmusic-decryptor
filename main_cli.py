#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QQ音乐解密工具 - 命令行版本
支持批量解密mflac/mgg文件，保留原始目录结构
"""

import argparse
import frida
import os
import hashlib
import sys
import json
import time
from datetime import datetime
import shutil
from pathlib import Path
import configparser
from metadata_utils import (
    extract_track_number_from_filename,
    add_track_number_to_flac,
    process_album_metadata,
    QQMusicAPIClient
)


class QQMusicDecryptorCLI:
    def __init__(self, config_path=None):
        """初始化配置"""
        self.config = self._load_config(config_path)
        
        # 从配置或命令行参数获取路径
        self.input_dir = None
        self.output_dir = None
        self.verbose = False
        self.max_retries = 3
        self.retry_delay = 2
        self.preserve_structure = True
        self.skip_existing = True
        self.verify_metadata = True

        # 从配置读取元数据处理模式
        self.metadata_processing_mode = self.config.get('OPTIONS', 'metadata_processing_mode', fallback='batch')
        self.skip_metadata_during_decrypt = self.config.getboolean('OPTIONS', 'skip_metadata_during_decrypt', fallback=True)

        # 新增：删除选项
        self.delete_source = True
        self.delete_empty_dirs = True
        self.delete_lyrics = True

        # 运行时状态
        self.session = None
        self.script = None
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None,
            'failed_files': []
        }

        # 新增：删除统计
        self.deleted_files = 0
        self.deleted_dirs = 0
        
        # 日志
        self.log_file = None
        self.log_messages = []
        
    def _load_config(self, config_path):
        """加载配置文件"""
        config = configparser.ConfigParser()
        
        # 默认配置
        config['PATHS'] = {
            'input_dir': 'G:\\QQMusic\\Download',
            'output_dir': 'G:\\QQMusic\\Decrypted'
        }
        config['LOGGING'] = {
            'log_level': 'INFO',
            'log_file': 'logs/decrypt.log',
            'save_stats': 'true'
        }
        config['OPTIONS'] = {
            'preserve_structure': 'true',
            'skip_existing': 'true',
            'max_retries': '3',
            'retry_delay': '2',
            'verify_metadata': 'true',
            'delete_source': 'true',
            'delete_empty_dirs': 'true',
            'delete_lyrics': 'true',
            'metadata_processing_mode': 'batch',
            'skip_metadata_during_decrypt': 'true'
        }
        config['NOTIFICATIONS'] = {
            'show_completion': 'true',
            'show_summary': 'true'
        }
        
        # 加载配置文件（如果存在）
        if config_path and os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
        
        return config
    
    def log(self, message, level='INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        # 保存到内存
        self.log_messages.append(log_message)
        
        # 输出到控制台
        if level in ['INFO', 'WARNING', 'ERROR'] or self.verbose:
            print(log_message)
        
        # 写入日志文件
        if self.log_file:
            try:
                self.log_file.write(log_message + '\n')
                self.log_file.flush()
            except:
                pass
    
    def connect_to_qqmusic(self):
        """连接到QQ音乐进程"""
        try:
            # 使用Windows命令获取QQ Music进程PID
            import subprocess
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq QQMusic.exe', '/FO', 'CSV'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log("未找到QQ Music进程", "ERROR")
                return False
            
            # 解析CSV输出
            lines = result.stdout.strip().split('\n')
            pids = []
            for line in lines[1:]:  # 跳过标题行
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1].strip('"'))
                        pids.append(pid)
                    except ValueError:
                        pass
            
            if not pids:
                self.log("未找到QQ Music进程", "ERROR")
                return False
            
            # 选择PID最小的进程（通常是主进程）
            target_pid = min(pids)
            
            if len(pids) > 1:
                self.log(f"发现 {len(pids)} 个QQ Music进程，选择PID {target_pid}", "INFO")
            else:
                self.log(f"找到QQ Music进程 (PID: {target_pid})", "INFO")
            
            # 附加到指定进程
            self.session = frida.attach(target_pid)
            self.log("成功连接到QQ音乐进程", "INFO")
            return True
        except Exception as e:
            self.log(f"连接QQ音乐进程失败: {e}", "ERROR")
            self.log("请确保: 1) QQ音乐正在运行 2) frida-server已启动", "ERROR")
            return False
    
    def load_decrypt_script(self):
        """加载Frida解密脚本"""
        script_path = os.path.join(os.path.dirname(__file__), "hook_qq_music.js")
        
        if not os.path.exists(script_path):
            self.log(f"未找到解密脚本: {script_path}", "ERROR")
            return False
        
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                script_code = f.read()
            
            self.script = self.session.create_script(script_code)
            self.script.load()
            self.log("解密脚本加载成功", "INFO")
            
            # 等待脚本完全加载
            time.sleep(1)
            return True
        except Exception as e:
            self.log(f"加载解密脚本失败: {e}", "ERROR")
            return False
    
    def get_output_path(self, input_file):
        """计算输出文件路径（保留目录结构）"""
        # 计算相对路径
        relative_path = os.path.relpath(input_file, self.input_dir)
        
        # 构建输出路径
        if self.preserve_structure:
            output_path = os.path.join(self.output_dir, relative_path)
        else:
            # 扁平化结构
            filename = os.path.basename(relative_path)
            output_path = os.path.join(self.output_dir, filename)
        
        # 转换扩展名
        output_path = os.path.splitext(output_path)[0]
        if input_file.lower().endswith('.mflac'):
            output_path += '.flac'
        elif input_file.lower().endswith('.mgg'):
            output_path += '.ogg'
        
        return output_path
    
    def is_already_converted(self, input_file, output_file):
        """检查文件是否已转换"""
        if not os.path.exists(output_file):
            return False
        
        if not self.skip_existing:
            return False
        
        # 检查输出文件是否比输入文件新
        try:
            input_mtime = os.path.getmtime(input_file)
            output_mtime = os.path.getmtime(output_file)
            
            if output_mtime >= input_mtime:
                self.log(f"文件已存在且较新，跳过: {os.path.basename(input_file)}", "INFO")
                return True
        except:
            pass
        
        return False
    
    def verify_flac_file(self, flac_file):
        """验证FLAC文件的有效性"""
        try:
            import flac
            with open(flac_file, 'rb') as f:
                flac_file_obj = flac.File(f)
                
                if not flac_file_obj.check():
                    return False
                
                return True
        except ImportError:
            self.log("FLAC验证库未安装，跳过验证", "WARNING")
            return True
        except Exception as e:
            self.log(f"FLAC验证失败: {e}", "WARNING")
            return False

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
                self.log(f"✓ 已删除源文件: {os.path.basename(input_file)}", "INFO")

            # 删除歌词文件（只检查源文件是否存在，不验证复制结果）
            if delete_lyrics:
                lyric_file = os.path.splitext(input_file)[0] + ".lrc"
                if os.path.exists(lyric_file):
                    os.remove(lyric_file)
                    deleted_count += 1
                    self.log(f"✓ 已删除歌词文件: {os.path.basename(lyric_file)}", "INFO")

        except Exception as e:
            self.log(f"删除文件失败: {e}", "WARNING")

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
                self.log(f"✓ 已删除空目录: {dir_path}", "INFO")

                # 递归删除父目录
                parent_dir = os.path.dirname(dir_path)
                deleted_count += self.cleanup_empty_dirs(parent_dir, root_dir)

        except Exception as e:
            self.log(f"删除目录失败: {e}", "WARNING")

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
                    self.log(f"✓ 已添加音轨号 {track_number}", "INFO")
                else:
                    self.log(f"✗ 添加音轨号失败", "WARNING")
            else:
                self.log(f"未找到音轨号，跳过音轨号添加", "DEBUG")
            
            # 步骤2：处理专辑元数据（封面、发行年份）
            self.log(f"获取专辑信息...", "INFO")
            api_client = QQMusicAPIClient()
            result = process_album_metadata(flac_file_path, api_client, use_cache=True)
            
            if result['success']:
                metadata = result.get('metadata', {})
                if metadata:
                    pub_year = metadata.get('pub_year')
                    if pub_year:
                        self.log(f"✓ 已添加发行年份 {pub_year}", "INFO")
                    
                    if metadata.get('cover_data'):
                        self.log(f"✓ 已嵌入封面到文件", "INFO")
                        self.log(f"✓ 已保存封面到 cover.jpg", "INFO")
            else:
                self.log(f"未找到专辑信息: {result['message']}", "WARNING")
        
        except Exception as e:
            self.log(f"添加元数据异常: {e}", "WARNING")
            return False

    def run_supplement_metadata(self):
        """
        运行元数据补充脚本

        处理整个输出目录，批量添加音轨号、封面、年份
        """
        import subprocess

        try:
            # 检查 supplement_album_metadata.py 是否存在
            script_path = os.path.join(os.path.dirname(__file__), 'supplement_album_metadata.py')

            if not os.path.exists(script_path):
                self.log(f"元数据脚本不存在: {script_path}", "WARNING")
                return

            # 构建命令
            cmd = ['python', script_path, self.output_dir]

            self.log(f"执行命令: {' '.join(cmd)}", "INFO")

            # 运行脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            # 输出脚本输出（只输出 info 级别）
            for line in result.stdout.split('\n'):
                if line.strip() and ('INFO' in line or '处理' in line):
                    self.log(line.strip(), "INFO")

            # 输出错误信息
            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.log(line.strip(), "ERROR")

            if result.returncode == 0:
                self.log("元数据处理成功", "INFO")
            else:
                self.log(f"元数据处理失败，错误代码: {result.returncode}", "ERROR")

        except Exception as e:
            self.log(f"执行元数据脚本异常: {e}", "ERROR")

    def decrypt_file(self, input_file, retry_count=0):
        """解密单个文件"""
        if retry_count >= self.max_retries:
            self.log(f"达到最大重试次数: {input_file}", "ERROR")
            return "failed_max_retries"
        
        # 获取输出路径
        output_file = self.get_output_path(input_file)
        
        # 创建输出目录
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 检查是否已转换
        if self.is_already_converted(input_file, output_file):
            return "skipped"
        
        # 获取文件大小
        try:
            file_size = os.path.getsize(input_file)
            file_size_mb = file_size / (1024 * 1024)
        except Exception as e:
            self.log(f"无法获取文件大小: {e}", "ERROR")
            return "failed"
        
        # 生成临时文件名
        filename = os.path.basename(input_file)
        output_ext = '.flac' if filename.lower().endswith('.mflac') else '.ogg'
        temp_file_name = hashlib.md5(filename.encode()).hexdigest() + output_ext
        temp_file_path = os.path.join(self.output_dir, temp_file_name)
        
        # 重试次数提示
        retry_info = f" (重试 {retry_count + 1}/{self.max_retries})" if retry_count > 0 else ""
        
        try:
            self.log(f"正在解密: {filename}", "INFO")
            self.log(f"输入: {input_file}", "INFO")
            self.log(f"输出: {output_file}", "INFO")
            self.log(f"文件大小: {file_size_mb:.2f} MB{retry_info}", "INFO")
            
            # 调用Frida解密函数
            try:
                result = self.script.exports_sync.decrypt(input_file, temp_file_path)
            except AttributeError as e:
                self.log(f"解密调用失败: {e}", "ERROR")
                result = "AttributeError: " + str(e)
            
            if "Success" in result:
                # 重命名为最终文件名
                os.rename(temp_file_path, output_file)
                
                # 验证输出文件
                if output_file.lower().endswith('.flac'):
                    if not self.verify_flac_file(output_file):
                        os.remove(output_file)
                        self.log("FLAC验证失败，删除文件", "ERROR")
                        raise Exception("FLAC validation failed")
                
                # 检查输出文件大小
                try:
                    output_size = os.path.getsize(output_file)
                    output_size_mb = output_size / (1024 * 1024)
                    ratio = (output_size / file_size) * 100
                    
                    self.log(f"输出文件大小: {output_size_mb:.2f} MB ({ratio:.1f}%)", "INFO")
                    
                    # 文件大小合理性检查（应该在原始大小的80-120%之间）
                    if ratio < 80 or ratio > 120:
                        self.log(f"警告: 文件大小异常 ({ratio:.1f}%)", "WARNING")
                except:
                    pass

                # 跳过解密时的元数据修改
                # 元数据将在所有文件解密完成后统一处理
                if not self.skip_metadata_during_decrypt and output_file.lower().endswith('.flac'):
                    self.add_flac_metadata(output_file)

                self.copy_lyrics_file(input_file, output_file)

                # === 新增：删除源文件和空目录 ===
                if self.delete_source:
                    # 删除源文件和歌词文件
                    deleted_count = self.delete_source_file(input_file, self.delete_lyrics)
                    self.deleted_files += deleted_count

                    # 删除空目录
                    if self.delete_empty_dirs:
                        file_dir = os.path.dirname(input_file)
                        deleted_dirs = self.cleanup_empty_dirs(file_dir, self.input_dir)
                        self.deleted_dirs += deleted_dirs
                # ===============================

                self.log(f"✓ 解密成功: {os.path.basename(output_file)}", "INFO")
                return "success"
            
            else:
                self.log(f"解密失败: {result}", "ERROR")
                raise Exception(result)
                
        except Exception as e:
            self.log(f"解密异常: {e}", "ERROR")
            
            # 清理临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            
            # 重试
            if retry_count < self.max_retries - 1:
                self.log(f"等待 {self.retry_delay} 秒后重试...", "INFO")
                time.sleep(self.retry_delay)
                return self.decrypt_file(input_file, retry_count + 1)
            else:
                return "failed"
    
    def scan_files(self):
        """扫描所有加密文件"""
        encrypted_files = []
        
        self.log(f"正在扫描目录: {self.input_dir}", "INFO")
        
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                file_ext = os.path.splitext(file)[-1].lower()
                if file_ext in [".mflac", ".mgg"]:
                    file_path = os.path.join(root, file)
                    encrypted_files.append(file_path)
        
        return encrypted_files
    
    def decrypt_all(self):
        """批量解密所有文件"""
        self.stats['start_time'] = time.time()
        
        # 检查输入目录
        if not os.path.exists(self.input_dir):
            self.log(f"错误: 输入目录不存在 - {self.input_dir}", "ERROR")
            return False
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 连接到QQ音乐
        if not self.connect_to_qqmusic():
            return False
        
        # 加载解密脚本
        if not self.load_decrypt_script():
            return False
        
        # 扫描文件
        files = self.scan_files()
        
        if not files:
            self.log("未找到任何.mflac或.mgg文件", "WARNING")
            return True
        
        self.stats['total'] = len(files)
        self.log(f"找到 {len(files)} 个加密文件", "INFO")
        
        # 批量解密
        for i, file_path in enumerate(files):
            progress = (i + 1) / len(files) * 100
            self.log(f"正在处理: {i + 1}/{len(files)} ({progress:.1f}%)", "INFO")
            self.log("-" * 60, "INFO")
            
            result = self.decrypt_file(file_path)
            self.stats[result] += 1
            
            if result == "failed":
                self.stats['failed_files'].append(file_path)
            
            self.log("", "INFO")
        
        # 结束时间
        self.stats['end_time'] = time.time()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        # 计算速度
        speed = 0
        if duration > 0:
            speed = self.stats['success'] / (duration / 60)
        
        self.stats['duration'] = duration
        self.stats['speed'] = speed

        # 解密完成后统一处理元数据（批量模式）
        if self.metadata_processing_mode == 'batch':
            self.log("=" * 60, "INFO")
            self.log("解密完成，开始统一处理元数据", "INFO")
            self.log("=" * 60, "INFO")

            # 调用批量元数据处理
            self.run_supplement_metadata()

            self.log("=" * 60, "INFO")
            self.log("元数据处理完成", "INFO")
            self.log("=" * 60, "INFO")

        # 打印完成通知
        self.print_completion_notice()

        # 保存统计信息
        self.save_stats()
        
        # 返回是否全部成功
        return self.stats['failed'] == 0
    
    def print_completion_notice(self):
        """打印完成通知"""
        duration_min = self.stats['duration'] / 60
        duration_sec = self.stats['duration'] % 60
        
        print("\n" + "="*60)
        print("  解密任务完成！")
        print("="*60)
        print(f"  总文件数: {self.stats['total']}")
        print(f"  成功: {self.stats['success']} [OK]")
        print(f"  失败: {self.stats['failed']} [FAIL]")
        print(f"  跳过: {self.stats['skipped']} [SKIP]")
        print(f"  处理时间: {int(duration_min)}分{int(duration_sec)}秒")
        print(f"  平均速度: {self.stats['speed']:.2f} 文件/分钟")
        print("="*60)

        if self.stats['failed'] > 0:
            print("\n  以下文件转换失败：")
            for file in self.stats['failed_files']:
                filename = os.path.basename(file)
                print(f"     - {filename}")
            print(f"\n  详细日志: {self.config['LOGGING']['log_file']}")

        print()
    
    def save_stats(self):
        """保存统计信息到JSON文件"""
        if self.config.getboolean('LOGGING', 'save_stats', fallback=True):
            stats_file = os.path.join(os.path.dirname(self.log_file.name), 'stats.json')
            
            stats_data = {
                'timestamp': datetime.now().isoformat(),
                'input_dir': self.input_dir,
                'output_dir': self.output_dir,
                'stats': self.stats,
                'cleanup': {
                    'deleted_files': self.deleted_files,
                    'deleted_dirs': self.deleted_dirs
                }
            }
            
            try:
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats_data, f, ensure_ascii=False, indent=2)
                self.log(f"统计信息已保存到: {stats_file}", "INFO")
            except Exception as e:
                self.log(f"保存统计信息失败: {e}", "WARNING")
    
    def disconnect(self):
        """断开连接"""
        if self.session:
            try:
                self.session.detach()
                self.log("已断开与QQMusic的连接", "INFO")
            except:
                pass
    
    def setup_logging(self):
        """设置日志文件"""
        log_file_path = self.config['LOGGING']['log_file']
        
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 打开日志文件
        try:
            self.log_file = open(log_file_path, 'a', encoding='utf-8')
            self.log(f"日志文件: {log_file_path}", "INFO")
        except Exception as e:
            print(f"警告: 无法打开日志文件: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='QQ音乐批量解密工具 - 命令行版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main_cli.py
  python main_cli.py --input "D:\\Music\\VipSongs" --output "D:\\Music\\Decrypted"
  python main_cli.py -i "D:\\input" -o "D:\\output" --verbose
  python main_cli.py --config "config.ini" --retries 5
        """
    )
    
    parser.add_argument('-i', '--input', help='输入目录（包含.mflac/.mgg文件）')
    parser.add_argument('-o', '--output', help='输出目录（保存解密后的文件）')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-r', '--retries', type=int, help='重试次数（默认: 3）')
    parser.add_argument('--no-skip', action='store_true', help='不跳过已存在的文件')
    parser.add_argument('--flat', action='store_true', help='不保留目录结构（扁平化输出）')
    
    args = parser.parse_args()
    
    # 创建解密器实例
    decryptor = QQMusicDecryptorCLI(config_path=args.config)
    
    # 设置日志
    decryptor.setup_logging()
    
    # 从配置或命令行参数获取设置
    decryptor.input_dir = args.input or decryptor.config['PATHS']['input_dir']
    decryptor.output_dir = args.output or decryptor.config['PATHS']['output_dir']
    decryptor.verbose = args.verbose
    decryptor.max_retries = args.retries or decryptor.config.getint('OPTIONS', 'max_retries')
    decryptor.retry_delay = decryptor.config.getint('OPTIONS', 'retry_delay')
    decryptor.preserve_structure = not args.flat and decryptor.config.getboolean('OPTIONS', 'preserve_structure')
    decryptor.skip_existing = not args.no_skip and decryptor.config.getboolean('OPTIONS', 'skip_existing')
    decryptor.verify_metadata = decryptor.config.getboolean('OPTIONS', 'verify_metadata')
    decryptor.delete_source = decryptor.config.getboolean('OPTIONS', 'delete_source', fallback=True)
    decryptor.delete_empty_dirs = decryptor.config.getboolean('OPTIONS', 'delete_empty_dirs', fallback=True)
    decryptor.delete_lyrics = decryptor.config.getboolean('OPTIONS', 'delete_lyrics', fallback=True)
    
    decryptor.log("="*60, "INFO")
    decryptor.log("QQ Music 批量解密工具 - CLI版本", "INFO")
    decryptor.log("="*60, "INFO")
    decryptor.log(f"输入目录: {decryptor.input_dir}", "INFO")
    decryptor.log(f"输出目录: {decryptor.output_dir}", "INFO")
    decryptor.log(f"保留目录结构: {decryptor.preserve_structure}", "INFO")
    decryptor.log(f"跳过已存在: {decryptor.skip_existing}", "INFO")
    decryptor.log(f"最大重试次数: {decryptor.max_retries}", "INFO")
    decryptor.log(f"重试延迟: {decryptor.retry_delay}秒", "INFO")
    decryptor.log("="*60, "INFO")
    
    # 执行解密
    try:
        success = decryptor.decrypt_all()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        decryptor.log("\n用户中断", "WARNING")
        exit_code = 130
    except Exception as e:
        decryptor.log(f"\n未预期的错误: {e}", "ERROR")
        import traceback
        decryptor.log(traceback.format_exc(), "ERROR")
        exit_code = 1
    finally:
        decryptor.disconnect()
        if decryptor.log_file:
            decryptor.log_file.close()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
