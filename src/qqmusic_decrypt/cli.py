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

"""
qqmusic-decrypt 命令行入口

全局命令，一键完成：解密音乐 → 补充专辑元数据
安装后可在任意位置执行: qqmusic-decrypt
"""

import os
import sys
import argparse

# ── 检测项目根目录 ──────────────────────────────────────────
# 当前文件: .../project_root/src/qqmusic_decrypt/cli.py
# 向上两级 = project_root
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _to_root():
    """切换到项目根目录并添加 src/ 到 Python 路径"""
    os.chdir(_PROJECT_ROOT)
    src_dir = os.path.join(_PROJECT_ROOT, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def _run_decrypt(verbose, remaining_argv):
    """执行解密"""
    from main_cli import main as decrypt_main

    print('=' * 60)
    print('  Step 1: 解密音乐文件')
    print('=' * 60)
    print()

    # 透传剩余参数给 main_cli
    sys.argv = ['qqmusic-decrypt'] + remaining_argv
    try:
        code = decrypt_main()
    finally:
        sys.argv = ['qqmusic-decrypt']  # 恢复

    if code:
        print('\n[错误] 解密失败，终止')
        return code

    print('\n[OK] 解密完成\n')
    return 0


def _run_supplement(output_dir, verbose):
    """执行专辑元数据补充"""
    from supplement_album_metadata import process_album_directory

    print('=' * 60)
    print('  Step 2: 补充专辑元数据')
    print('=' * 60)
    print()

    if not os.path.isdir(output_dir):
        print(f'  [跳过] 输出目录不存在: {output_dir}')
        return 0

    # 查找输出目录下的专辑子目录
    items = os.listdir(output_dir)
    albums = [d for d in items if os.path.isdir(os.path.join(output_dir, d))]

    if not albums:
        print(f'  直接处理: {output_dir}')
        process_album_directory(output_dir)
    else:
        print(f'  找到 {len(albums)} 个专辑目录')
        for album in albums:
            album_path = os.path.join(output_dir, album)
            print(f'  ─ {album}')
            process_album_directory(album_path)

    print()
    print('[OK] 元数据补充完成')
    return 0


def main():
    _to_root()

    parser = argparse.ArgumentParser(
        description='QQ音乐 一键解密 + 补充元数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  qqmusic-decrypt                   # 使用config.ini配置执行
  qqmusic-decrypt --skip-decrypt    # 只补充元数据
  qqmusic-decrypt --skip-supplement # 只解密
  qqmusic-decrypt --verbose         # 详细输出
        """,
    )
    parser.add_argument('--skip-decrypt', action='store_true', help='跳过解密，只补充元数据')
    parser.add_argument('--skip-supplement', action='store_true', help='跳过元数据补充，只解密')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('-o', '--output', help='输出目录（覆盖config.ini中的配置）')

    args, remaining = parser.parse_known_args()

    # ── 读取配置 ──
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')

    input_dir = config.get('PATHS', 'input_dir', fallback=None)
    output_dir = args.output or config.get('PATHS', 'output_dir', fallback='G:/QQMusic/Decrypted')

    if not input_dir and not args.skip_decrypt:
        print('[错误] 未配置输入目录，请在 config.ini 中设置 [PATHS] input_dir')
        return 1

    # ── Step 1: 解密 ──
    if not args.skip_decrypt:
        code = _run_decrypt(args.verbose, remaining)
        if code:
            return code

    # ── Step 2: 补充元数据 ──
    if not args.skip_supplement:
        code = _run_supplement(output_dir, args.verbose)
        if code:
            return code

    print()
    print('=' * 60)
    print('  全部完成！')
    print('=' * 60)
    return 0



# ── qqmusic-meta: 仅补充专辑元数据 ─────────────────────────


def _process_directory(album_dir, verbose=False):
    """处理单个专辑目录的元数据补充"""
    from supplement_album_metadata import process_album_directory

    if not os.path.isdir(album_dir):
        print(f'[错误] 目录不存在: {album_dir}')
        return 1

    print(f'处理目录: {album_dir}')
    print()

    # 检查是否有子目录
    items = os.listdir(album_dir)
    albums = [d for d in items if os.path.isdir(os.path.join(album_dir, d))]

    if not albums:
        process_album_directory(album_dir)
    else:
        print(f'找到 {len(albums)} 个专辑目录')
        for album in albums:
            album_path = os.path.join(album_dir, album)
            print(f'  ─ {album}')
            process_album_directory(album_path)

    print()
    print('处理完成')
    return 0


def supplement_main():
    """qqmusic-meta 入口：补充专辑元数据"""
    _to_root()

    parser = argparse.ArgumentParser(
        description='补充FLAC专辑元数据（封面+发行年份）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  qqmusic-meta                          # 使用config.ini的输出目录
  qqmusic-meta "D:/MyMusic/Decrypted"   # 指定目录
  qqmusic-meta -v                       # 详细输出
        """,
    )
    parser.add_argument('album_dir', nargs='?', help='专辑目录（默认使用config.ini的输出目录）')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')

    args = parser.parse_args()

    # 确定目录
    if args.album_dir:
        album_dir = args.album_dir
    else:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        album_dir = config.get('PATHS', 'output_dir', fallback='G:/QQMusic/Decrypted')
        print(f'使用默认目录: {album_dir}')

    return _process_directory(album_dir, args.verbose)


# ── qqmusic-gui: 启动GUI界面 ──────────────────────────────


def gui_main():
    """qqmusic-gui 入口：启动GUI界面"""
    _to_root()

    gui_file = os.path.join(_PROJECT_ROOT, 'src', 'gui', 'main_gui.py')
    if not os.path.exists(gui_file):
        print(f'[错误] 找不到GUI文件: {gui_file}')
        return 1

    print('启动GUI...')
    print()

    import subprocess
    import sys as _sys

    if _sys.platform == 'win32':
        # Windows上用 pythonw 隐藏控制台
        subprocess.Popen(['pythonw', gui_file], shell=True)
    else:
        subprocess.Popen(['python3', gui_file])

    print('GUI已启动')
    return 0


if __name__ == '__main__':
    sys.exit(main())
