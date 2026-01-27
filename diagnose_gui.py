#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUI 诊断脚本
帮助诊断GUI启动问题
"""

import sys
import os

def check_environment():
    """检查运行环境"""
    print("="*60)
    print("GUI 环境诊断")
    print("="*60)
    print()

    # 检查1: Python版本
    print("[1/6] 检查 Python 版本...")
    print(f"      Python 版本: {sys.version}")
    print(f"      Python 路径: {sys.executable}")
    if sys.version_info >= (3, 8):
        print("      [PASS] Python 版本符合要求 (3.8+)")
    else:
        print("      [FAIL] Python 版本过低，需要 3.8+")
        return False
    print()

    # 检查2: frida包
    print("[2/6] 检查 frida 包...")
    try:
        import frida
        print(f"      Frida 版本: {frida.__version__}")
        if frida.__version__ == "16.7.10":
            print("      [PASS] Frida 版本正确 (16.7.10)")
        else:
            print(f"      [WARN] Frida 版本不匹配 (当前: {frida.__version__}, 期望: 16.7.10)")
    except ImportError:
        print("      [FAIL] Frida 包未安装")
        print("      请运行: pip install frida==16.7.10")
        return False
    print()

    # 检查3: tkinter
    print("[3/6] 检查 tkinter 库...")
    try:
        import tkinter as tk
        print("      [PASS] tkinter 可用")
        # 测试创建窗口
        try:
            root = tk.Tk()
            root.destroy()
            print("      [PASS] tkinter 测试成功")
        except Exception as e:
            print(f"      [FAIL] tkinter 测试失败: {e}")
            return False
    except ImportError:
        print("      [FAIL] tkinter 未安装")
        print("      tkinter 是Python标准库，应该自动包含")
        return False
    print()

    # 检查4: GUI文件
    print("[4/6] 检查 GUI 文件...")
    gui_file = "gui_backup/main_gui.py"
    if os.path.exists(gui_file):
        print(f"      [PASS] GUI 文件存在: {gui_file}")
    else:
        print(f"      [FAIL] GUI 文件不存在: {gui_file}")
        return False
    print()

    # 检查5: Frida脚本
    print("[5/6] 检查 Frida 脚本...")
    hook_file = "hook_qq_music.js"
    if os.path.exists(hook_file):
        print(f"      [PASS] Frida 脚本存在: {hook_file}")
    else:
        print(f"      [FAIL] Frida 脚本不存在: {hook_file}")
        return False
    print()

    # 检查6: 进程状态
    print("[6/6] 检查运行进程...")
    try:
        import psutil
        frida_running = any(p.name() == 'frida-server.exe' for p in psutil.process_iter())
        qqmusic_running = any(p.name() == 'QQMusic.exe' for p in psutil.process_iter())

        if frida_running:
            print("      [PASS] frida-server 正在运行")
        else:
            print("      [FAIL] frida-server 未运行")
            print("      请以管理员身份运行: start_frida_server.bat")

        if qqmusic_running:
            print("      [PASS] QQ Music 正在运行")
        else:
            print("      [FAIL] QQ Music 未运行")
            print("      请启动 QQ Music 客户端")

        if not (frida_running and qqmusic_running):
            print()
            print("      注意: 这些进程不是GUI启动的必需条件，")
            print("      但是解密功能需要它们运行。")
    except ImportError:
        print("      [WARN] psutil 未安装，无法检查进程")
        print("      请运行: pip install psutil")
    print()

    return True

def test_gui_import():
    """测试GUI模块导入"""
    print("="*60)
    print("GUI 模块测试")
    print("="*60)
    print()

    print("尝试导入 GUI 模块...")
    try:
        sys.path.insert(0, '.')
        from gui_backup import main_gui
        print("      [PASS] GUI 模块导入成功")
        return True
    except Exception as e:
        print(f"      [FAIL] GUI 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print()
    print("QQ Music 解密工具 - GUI 诊断")
    print()
    print("此脚本将诊断GUI启动所需的环境")
    print()

    # 检查环境
    env_ok = check_environment()

    if env_ok:
        # 测试GUI模块
        print()
        gui_ok = test_gui_import()

        if gui_ok:
            print()
            print("="*60)
            print("诊断完成！")
            print("="*60)
            print()
            print("所有检查通过，可以启动GUI。")
            print()
            print("启动方法:")
            print("  双击运行: quick_start_gui.bat")
            print("  或运行: pythonw gui_backup/main_gui.py")
            print()
        else:
            print()
            print("="*60)
            print("诊断失败")
            print("="*60)
            print()
            print("GUI模块存在问题，请查看上面的错误信息。")
            print()
    else:
        print()
        print("="*60)
        print("诊断失败")
        print("="*60)
        print()
        print("环境不满足要求，请根据上面的提示修复问题。")
        print()

    input("按任意键退出...")

if __name__ == "__main__":
    main()
