#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接启动GUI并捕获错误
"""

import sys
import os
import traceback

print("正在启动GUI...")
print("="*60)

try:
    # 添加当前目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # 导入GUI模块
    from gui_backup import main_gui

    print("GUI模块加载成功")
    print("正在创建主窗口...")
    print()

    # 创建GUI应用
    import tkinter as tk
    root = tk.Tk()
    app = main_gui.QQMusicDecryptorGUI(root)
    root.mainloop()

except Exception as e:
    print()
    print("="*60)
    print("启动失败！")
    print("="*60)
    print()
    print("错误信息:")
    print(str(e))
    print()
    print("详细错误:")
    traceback.print_exc()
    print()
    print("="*60)
    input("按任意键退出...")
