#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Precise Fix Script for GUI
Fixes two specific issues:
1. Change output directory default value
2. Fix directory structure preservation logic
"""

import os
import shutil

print("="*60)
print("Precise Fix Script")
print("="*60)
print()

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

# Backup original file
backup_file = gui_file + ".bak"
if not os.path.exists(backup_file):
    shutil.copy2(gui_file, backup_file)
    print(f"[Backup] Original file backed up to: {backup_file}")
else:
    print("[Backup] Backup already exists, skipping")

# Read file
print("[Step 1] Reading GUI file...")
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f"         Total lines: {len(lines)}")

# Apply fixes
print("[Step 2] Applying fixes...")

fixed_lines = []
fix_count = 0

for i, line in enumerate(lines, 1):  # Start from line 1
    # Fix 1: Change default output directory (around line 99)
    if i == 99 and 'D:\\\\Decrypted\\\\Music' in line:
        fixed_lines.append("G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")
        fix_count += 1
        print(f"         Line {i}: Changed output directory default")
    # Fix 2: Fix directory structure preservation (around line 56)
    elif i == 56 and 'output_file_path = os.path.join(output_dir, output_file)' in line:
        # Insert BEFORE this line the logic to preserve directory structure
        fixed_lines.append("                # Preserve directory structure\n")
        fixed_lines.append("                relative_path = os.path.relpath(encrypted_file, input_dir)\n")
        fixed_lines.append("                output_file_path = os.path.join(output_dir, relative_path)\n")
        # Comment out old line
        fixed_lines.append("                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE - Commented out\n")
        fix_count += 2
        print(f"         Line {i}: Fixed directory structure preservation")
    else:
        fixed_lines.append(line)

if fix_count == 0:
    print("\n[ERROR] No fixes applied! The expected lines were not found.")
    import sys
    sys.exit(1)

print(f"\n[Success] Applied {fix_count} fixes!")

# Write modified file
print("[Step 3] Writing modified file...")
modified_content = ''.join(fixed_lines)

with open(gui_file, 'w', encoding='utf-8') as f:
    f.write(modified_content)

print("         File written successfully")

print()
print("="*60)
print("Fix completed successfully!")
print("="*60)
print()
print("Changes made:")
print("  1. Output directory: D:\\\\Decrypted\\Music -> G:\\QQMusic\\Decrypted\\VipSongsDownload")
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
