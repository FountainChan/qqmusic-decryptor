#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Frida Connection Diagnostic
"""

import frida
import subprocess
import sys

print("="*60)
print("Frida Connection Diagnostic")
print("="*60)

# Check 1: frida-server process
print("\n[Check 1] frida-server process")
try:
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    if 'frida-server.exe' in result.stdout:
        print("PASS: frida-server is running")
    else:
        print("FAIL: frida-server is NOT running!")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Check failed: {e}")
    sys.exit(1)

# Check 2: QQ Music process
print("\n[Check 2] QQ Music process")
try:
    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq QQMusic.exe', '/FO', 'CSV'],
                        capture_output=True, text=True)
    if result.returncode == 0 and 'QQMusic.exe' in result.stdout:
        pids = []
        for line in result.stdout.strip().split('\n'):
            parts = line.split(',')
            if len(parts) >= 2:
                try:
                    pid = int(parts[1].strip('"'))
                    pids.append(pid)
                except ValueError:
                    pass
        print(f"PASS: Found {len(pids)} QQ Music process(es): {pids}")
    else:
        print("FAIL: QQ Music is NOT running")
except Exception as e:
    print(f"FAIL: Check failed: {e}")

# Check 3: Frida version
print("\n[Check 3] Frida version")
try:
    print(f"   Frida version: {frida.__version__}")
except:
    print("   FAIL: Cannot get version")

# Check 4: Test connection to frida-server
print("\n[Check 4] Testing connection to frida-server")
try:
    print("   Trying to connect to frida-server...")
    device = frida.get_local_device()
    print(f"PASS: Successfully connected to device: {device}")
except Exception as e:
    print(f"FAIL: Connection to frida-server failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("\nDiagnostic complete")
print("If all checks pass, Frida environment is OK")
print("If there are issues, please fix them before trying again")
