import os
import shutil

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
backup_file = gui_file + ".final_fixed"

# Create backup
shutil.copy2(gui_file, backup_file)
print(f"Backup created: {backup_file}")

# Read file
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Fix 1: Line 99 - Output directory default
print("\n=== Fix 1: Output directory default ===")
fixed_1 = False
for i, line in enumerate(lines):
    if i == 99 and 'D:\\\\Decrypted\\\\Music' in line:
        lines[i] = '                self.output_path.set("G:\\QQMusic\\Decrypted\\\\VipSongsDownload")'
        print(f"Fixed line {i}: Output directory default value")
        fixed_1 = True
        break

if not fixed_1:
    print("ERROR: Could not find line 99 to fix output directory default")

# Fix 2: Lines 56-57 - Directory structure preservation
print("\n=== Fix 2: Directory structure preservation ===")
fixed_2 = False
for i, line in enumerate(lines):
    if i == 56 and 'output_file_path = os.path.join(output_dir, output_file)' in line:
        # Comment out old line
        lines[i] = '                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE\n'
        # Insert new logic BEFORE this line
        new_lines = lines[:i]
        new_lines.append('                # Preserve directory structure\n')
        new_lines.append('                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
        new_lines.append('                output_file_path = os.path.join(output_dir, relative_path)\n')
        new_lines.extend(lines[i+1:])
        lines = new_lines
        fixed_2 = True
        print(f"Fixed lines {i}-{i+3}: Directory structure preservation")
        break

if not fixed_2:
    print("ERROR: Could not find line 56 to fix directory structure")

# Write fixed file
print("\n=== Writing fixed file ===")
with open(gui_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"Fixed file written: {gui_file}")
print("\n=== Summary ===")
print("1. Output directory: D:\\\\Decrypted\\\\Music -> G:\\QQMusic\\Decrypted\\\\VipSongsDownload")
print("2. Directory structure: Added os.path.relpath() to preserve full path hierarchy")
print("\nNext: Run GUI")
