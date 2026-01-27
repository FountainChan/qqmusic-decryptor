#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test GUI path fix"""

import os

def test_file_existence():
    """Test if key files exist"""
    print("Testing key files...")
    
    files = [
        "run_gui_simple.bat",
        "launch_gui.bat",
        "gui_backup/main_gui.py",
        "config.ini",
        "hook_qq_music.js",
    ]
    
    all_exist = True
    for file in files:
        exists = os.path.exists(file)
        status = "OK" if exists else "FAIL"
        print(f"  [{status}] {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_path():
    """Test if GUI module path works"""
    print("\nTesting GUI module path...")
    
    try:
        import sys
        os.chdir(r"D:\WorkDev\qqmusic_decryptor")
        sys.path.insert(0, 'gui_backup')
        
        # Just check if file exists and is readable
        with open("gui_backup/main_gui.py", 'r', encoding='utf-8') as f:
            content = f.read()
            if "class QQMusicDecryptorGUI" in content:
                print("  [OK] GUI file contains expected class")
                return True
            else:
                print("  [FAIL] GUI file structure incorrect")
                return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

def main():
    print("=" * 50)
    print("  GUI Path Fix Test")
    print("=" * 50)
    print()
    
    result1 = test_file_existence()
    result2 = test_path()
    
    print("\n" + "=" * 50)
    print("  Summary")
    print("=" * 50)
    print(f"  File existence: {'PASS' if result1 else 'FAIL'}")
    print(f"  Path test: {'PASS' if result2 else 'FAIL'}")
    print()
    
    if result1 and result2:
        print("All tests passed! You can run run_gui_simple.bat")
        return 0
    else:
        print("Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
