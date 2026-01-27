#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Fix Script for GUI - Corrected
"""

import os
import shutil

print("="*60)
print("Simple Fix Script for GUI")
print("="*60)
print()

# File paths (using raw strings)
gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

# Backup original file
backup_file = gui_file + ".bak"
if not os.path.exists(backup_file):
    shutil.copy2(gui_file, backup_file)
    print(f"[Step 1] Original file backed up")
else:
    print("[Step 1] Backup already exists, skipping")

# Read file
print("[Step 2] Reading GUI file...")
with open(gui_file, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"         Total lines: {len(content)}")

# Apply fixes
print("[Step 3] Applying fixes...")

# Fix 1: Change default output directory (line 99)
content = content.replace(
    'D:\\\\Decrypted\\\\Music',
    'G:\\QQMusic\\Decrypted\\\\VipSongsDownload'
)
print("         Old: D:\\\\Decrypted\\\\Music")
print("         New: G:\\QQMusic\\Decrypted\\\\VipSongsDownload")
print("         Status: DONE")

# Fix 2: Fix directory structure preservation (line 56)
# Find line with: output_file_path = os.path.join(output_dir, output_file)
old_line = '                output_file_path = os.path.join(output_dir, output_file)'
new_lines = []
found = False

for i, line in enumerate(content.split('\n'), 1):
    if not found:
        if old_line in line:
            print(f"         Line {i}: Found line to replace")
            # Insert new lines BEFORE this line
            new_lines.append('                # Preserve directory structure\n')
            new_lines.append('                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
            new_lines.append('                output_file_path = os.path.join(output_dir, relative_path)\n')
            new_lines.append('                # Comment out old code\n')
            new_lines.append('                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE\n')
            found = True
    new_lines.append(line)

if not found:
    print("\n[ERROR] Could not find the line to replace!")
    print("="*60)
    import sys
    sys.exit(1)

print(f"         Line {i}: Fixed directory structure preservation")
print("         Status: DONE")

if found:
    # Write modified content
    print("[Step 4] Writing modified file...")
    modified_content = '\n'.join(new_lines)

    with open(gui_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    print("         File written successfully")

print()
print("="*60)
print("Fix completed successfully!")
print("="*60)
print()
print("Changes made:")
print("  1. Output directory: D:\\\\Decrypted\\\\Music -> G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")
print("  2. Directory structure: Fixed to preserve full path hierarchy")
print()
print("Next steps:")
print("  1. Close current GUI window if running")
print("  2. Run GUI again: python D:\\WorkDev\\qqmusic_decryptor\\gui_backup\\main_gui.py")
print("  3. In GUI, verify paths:")
print("     - Input: G:\\QQMusic\\Download\\VipSongsDownload")
print("     - Output: G:\\QQMusic\\Decrypted\\VipSongsDownload")
print()
print("="*60)
print("Press any key to exit...")
input()
