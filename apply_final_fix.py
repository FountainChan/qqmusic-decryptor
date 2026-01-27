import os

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
backup_file = gui_file + ".fixed"

# Read file
with open(gui_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Output directory default (line 99)
# Old: self.output_path.set("D:\\Decrypted\\Music")
# New: self.output_path.set("G:\\QQMusic\\Decrypted\\VipSongsDownload")
content = content.replace('self.output_path.set("D:\\\\Decrypted\\Music")', 
                      'self.output_path.set("G:\\QQMusic\\Decrypted\\VipSongsDownload")')

# Fix 2: Directory structure preservation (line 56)
# Old: output_file_path = os.path.join(output_dir, output_file)
# New: Insert before line 56
old_line = '                output_file_path = os.path.join(output_dir, output_file)'
new_lines = '''                # Preserve directory structure
                relative_path = os.path.relpath(encrypted_file, input_dir)
                output_file_path = os.path.join(output_dir, relative_path)
                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE'''

content = content.replace(old_line, new_lines)

# Write fixed file
with open(gui_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("=== Fix Applied ===")
print("1. Output directory: D:\\\\Decrypted\\Music -> G:\\QQMusic\\Decrypted\\VipSongsDownload")
print("2. Directory structure: Fixed to preserve full path hierarchy")
print("\nNext: Run GUI")
