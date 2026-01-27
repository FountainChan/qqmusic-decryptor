import os
import shutil

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
backup_file = gui_file + ".bak"

if not os.path.exists(backup_file):
    shutil.copy2(gui_file, backup_file)
    print("Backup created")
else:
    print("Backup exists")

# Read
with open(gui_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: output directory
content = content.replace('D:\\\\Decrypted\\\\Music', 'G:\\QQMusic\\Decrypted\\\\VipSongsDownload')

# Fix 2: directory structure
old_code = 'output_file_path = os.path.join(output_dir, output_file)'
new_code = '''                relative_path = os.path.relpath(encrypted_file, input_dir)
                output_file_path = os.path.join(output_dir, relative_path)
                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE'''

content = content.replace(old_code, new_code)

# Write
with open(gui_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fix applied!")
print("1. Output directory: G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")
print("2. Directory structure: Preserved")
