import os

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"
backup_file = gui_file + ".bak"

# Step 1: Read original file
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Step 2: Apply fixes
fixed_lines = []

for i, line in enumerate(lines):
    # Fix 1: Line 99 - Output directory default
    if i == 99 and 'D:\\\\Decrypted\\\\Music' in line:
        fixed_lines.append('                self.output_path.set("G:\\QQMusic\\Decrypted\\\\VipSongsDownload")')
        print(f"Fixed line 99: Output directory default value")
    elif i == 99:
        fixed_lines.append(line)
    
    # Fix 2: Line 56-57 - Directory structure preservation
    elif i == 56 and 'output_file_path = os.path.join(output_dir, output_file)' in line:
        # Comment out old line
        fixed_lines.append('                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE\n')
        # Add new lines to preserve directory structure
        fixed_lines.append('                # Preserve directory structure\n')
        fixed_lines.append('                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
        fixed_lines.append('                output_file_path = os.path.join(output_dir, relative_path)\n')
        print(f"Fixed line 56: Directory structure preservation")
    elif i == 57:
        fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Step 3: Write modified content
with open(gui_file, 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("=== Fix Summary ===")
print("1. Output directory: D:\\\\Decrypted\\\\Music -> G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")
print("2. Directory structure: Fixed to preserve full path hierarchy")
print("3. Modified file:", gui_file)
print("\nNext steps:")
print("1. Run GUI: python D:\\WorkDev\\qqmusic_decryptor\\gui_backup\\main_gui.py")
print("2. Verify paths:")
print("   - Input: G:\\QQMusic\\Download\\VipSongsDownload")
print("   - Output: G:\\QQMusic\\Decrypted\\VipSongsDownload")
