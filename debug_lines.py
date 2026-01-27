#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug Fix Script
"""

import os

print("="*60)
print("Debug: Show lines around line 256")
print("="*60)
print()

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[245:270], 1):  # Show lines 245-270
        print(f"{i+1}: {repr(line)}")
