#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QQ音乐解密技能 - 快速启动脚本
当用户说"转换音乐"等关键词时调用此脚本
"""

import os
import sys
import subprocess
import time

def check_prerequisites():
    """检查前置条件"""
    checks = []

    # 检查 Python
    try:
        import sys
        print(f"[OK] Python 版本: {sys.version.split()[0]}")
        checks.append(True)
    except:
        print("[FAIL] Python 未安装")
        checks.append(False)

    # 检查 frida
    try:
        import frida
        print(f"[OK] frida 已安装: {frida.__version__}")
        checks.append(True)
    except ImportError:
        print("[FAIL] frida 未安装")
        checks.append(False)

    # 检查 mutagen
    try:
        from mutagen.flac import FLAC
        print("[OK] mutagen 已安装")
        checks.append(True)
    except ImportError:
        print("[FAIL] mutagen 未安装")
        checks.append(False)

    # 检查 frida-server
    try:
        result = subprocess.run(['frida-ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] frida-server 正在运行")
            checks.append(True)
        else:
            print("[FAIL] frida-server 未运行")
            checks.append(False)
    except FileNotFoundError:
        print("[FAIL] frida 命令未找到")
        checks.append(False)

    # 检查 QQ Music
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq QQMusic.exe'],
                            capture_output=True, text=True)
        if 'QQMusic.exe' in result.stdout:
            print("[OK] QQ Music 正在运行")
            checks.append(True)
        else:
            print("[FAIL] QQ Music 未运行")
            checks.append(False)
    except:
        print("[FAIL] 无法检查 QQ Music 状态")
        checks.append(False)

    return all(checks)

def start_gui():
    """启动 GUI 解密工具"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    bat_file = os.path.join(project_dir, 'run_gui_simple.bat')

    if not os.path.exists(bat_file):
        print(f"错误: 找不到 {bat_file}")
        return False

    print(f"\n启动 GUI: {bat_file}")
    try:
        subprocess.Popen([bat_file], shell=True)
        print("[OK] GUI 已启动")
        return True
    except Exception as e:
        print(f"[FAIL] 启动失败: {e}")
        return False

def start_cli():
    """启动 CLI 解密工具"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    bat_file = os.path.join(project_dir, 'auto_decrypt.bat')

    if not os.path.exists(bat_file):
        print(f"错误: 找不到 {bat_file}")
        return False

    print(f"\n启动 CLI: {bat_file}")
    try:
        subprocess.Popen([bat_file], shell=True)
        print("[OK] CLI 已启动")
        return True
    except Exception as e:
        print(f"[FAIL] 启动失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("QQ音乐解密工具 - 技能启动器")
    print("=" * 60)
    print()

    print("检查前置条件:")
    print("-" * 60)
    all_ok = check_prerequisites()
    print("-" * 60)
    print()

    if not all_ok:
        print("\n前置条件检查失败！")
        print("\n请确保:")
        print("1. Python 3.8+ 已安装")
        print("2. 依赖已安装: pip install -r requirements.txt")
        print("3. frida-server 正在运行（以管理员身份运行 start_frida_server.bat）")
        print("4. QQ Music 客户端已启动并登录 VIP")
        print("\n按任意键退出...")
        input()
        sys.exit(1)

    print("\n前置条件检查通过！")
    print()

    # 询问启动方式
    print("请选择启动方式:")
    print("1. GUI 模式（推荐，图形界面）")
    print("2. CLI 模式（命令行）")
    print()

    choice = input("请输入选项 (1 或 2，默认 1): ").strip() or "1"

    if choice == "1":
        success = start_gui()
    elif choice == "2":
        success = start_cli()
    else:
        print("无效选项，默认使用 GUI 模式")
        success = start_gui()

    if success:
        print("\n解密工具已启动！")
        print("\n提示:")
        if choice == "1":
            print("- 在 GUI 中配置输入/输出目录")
            print("- 点击'开始解密'按钮")
        else:
            print("- CLI 将自动处理配置文件中的路径")
        print("\n日志文件: logs/decrypt.log")
        print("\n按任意键退出...")
        input()
    else:
        print("\n启动失败！请检查错误信息。")
        print("\n按任意键退出...")
        input()
        sys.exit(1)

if __name__ == "__main__":
    main()
