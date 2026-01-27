#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File Status Checker - Check current GUI file status
"""

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

print("="*60)
print("GUI File Status Checker")
print("="*60)
print()

try:
    with open(gui_file, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        
    print(f"File read successfully. Total lines: {len(lines)}")
    print()
    
    # Check Fix 1: Line 99 - Output directory
    print("[Check 1] Line 99 - Output directory default value")
    for i, line in enumerate(lines):
        if i == 99:
            print(f"Line {i}: {repr(line[:120])}")
            if 'VipSongsDownload' in line:
                if 'G:\\QQMusic' in line:
                    print("  ✓ Contains correct path")
                else:
                    print("  ✗ Contains wrong path")
            break
    
    # Check Fix 2: Line 56 - Directory structure
    print()
    print("[Check 2] Lines 55-60 - Directory structure preservation")
    for i in range(55, 65):
        if i < len(lines):
            line = lines[i]
            if 'relative_path = os.path.relpath' in line:
                print(f"Line {i}: {repr(line[:120])}")
                print("  ✓ Found directory structure preservation code!")
            elif i == 56 and 'output_file_path = os.path.join(output_dir, output_file)' in line:
                print(f"Line {i}: {repr(line[:120])}")
                print("  ✗ Still has OLD code")
    
    print()
    print("="*60)
    print("Summary:")
    print("="*60)
    print()
    
except Exception as e:
    print(f"Error reading file: {e}")
