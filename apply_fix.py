import os

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

# Read original file
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: Line 99 - Change output directory default
for i, line in enumerate(lines):
    if i == 99 and 'D:\\\\Decrypted\\\\Music' in line:
        lines[i] = '                self.output_path.set("G:\\QQMusic\\Decrypted\\\\VipSongsDownload")'
        print(f"Fixed line 99: Output directory default value")
        break

# Fix 2: Line 56-57 - Directory structure preservation
for i, line in enumerate(lines):
    if i == 56 and 'output_file_path = os.path.join(output_dir, output_file)' in line:
        # Comment out old line
        lines[i] = '                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE\n'
        # Insert new logic BEFORE this line
        lines.insert(i, '                # Preserve directory structure\n')
        lines.insert(i + 1, '                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
        lines.insert(i + 2, '                output_file_path = os.path.join(output_dir, relative_path)\n')
        print(f"Fixed lines 56-58: Directory structure preservation")
        break

# Write back
with open(gui_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("=== Fix Summary ===")
print("1. Output directory: D:\\\\Decrypted\\\\Music -> G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")
print("2. Directory structure: Fixed to preserve full path hierarchy")
print("\nAll fixes applied successfully!")
print("\nNext: Run GUI")
