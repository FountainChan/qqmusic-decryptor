#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUI Status Check Script
"""

import subprocess
import sys

print("="*60)
print("GUI Status Check")
print("="*60)
print()

# Method 1: Check Python processes
print("[Method 1] Check Python processes...")
try:
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    python_processes = []
    for line in result.stdout.split('\n'):
        if 'python.exe' in line.lower():
            python_processes.append(line.strip())
    
    if python_processes:
        print(f"Found {len(python_processes)} python process(es):")
        for proc in python_processes:
            print(f"  {proc}")
    else:
        print("No Python process found")
except Exception as e:
    print(f"Check failed: {e}")

print()

# Method 2: Check GUI window
print("[Method 2] Check GUI window...")
print("Please manually check:")
print("1. Can you see GUI window open?")
print("2. Can you see Input and Output directory selection boxes?")
print("3. Can you see Start Decryption button?")
print()
print("If all above are visible, GUI is running")
print("If window is open but no response, try manually clicking Start")
print()
print("="*60)
print()

# Manual start options
print("If GUI is not running, try manual start:")
print()
print("Option 1: Use run_gui.bat")
print("  cd D:\\WorkDev\\qqmusic_decryptor\\gui_backup")
print("  python main_gui.py")
print()
print("Option 2: Direct Python script")
print("  cd D:\\WorkDev\\qqmusic_decryptor\\gui_backup")
print("  python main_gui.py &")
print()
print("="*60)
