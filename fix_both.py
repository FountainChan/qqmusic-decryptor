import os

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
backup_file = gui_file + ".bak"

# Backup
if not os.path.exists(backup_file):
    os.system(f'copy "{gui_file}" "{backup_file}"')
    print(f"Backup created: {backup_file}")

# Read and modify
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: Output directory default value (line 99)
for i, line in enumerate(lines, 1):
    if 'self.output_path.set("D:\\\\Decrypted\\\\Music")' in line:
        lines[i] = '                self.output_path.set("G:\\QQMusic\\Decrypted\\\\VipSongsDownload")'
        print(f"Fixed line {i}: Output directory default value")
        break

# Fix 2: Directory structure (line 56)
for i, line in enumerate(lines, 1):
    if 'output_file_path = os.path.join(output_dir, output_file)' in line:
        # Add new lines BEFORE this line
        new_lines = lines[:i]
        new_lines.append('                # Calculate relative path to preserve directory structure\n')
        new_lines.append('                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
        new_lines.append('                output_file_path = os.path.join(output_dir, relative_path)\n')
        new_lines.extend(lines[i:])
        lines = new_lines
        break

# Write
with open(gui_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixes applied successfully!")
print("1. Output directory: G:\\QQMusic\\Decrypted\\VipSongsDownload")
print("2. Directory structure: Preserved")
print("\nNext: Run GUI: python D:\\WorkDev\\qqmusic_decryptor\\gui_backup\\main_gui.py")
