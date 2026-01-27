import os

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

# Read file
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: Line 99 - Output directory default value
print("Fix 1: Output directory default value")
for i, line in enumerate(lines):
    if i == 99 and 'output_path.set' in line and 'DecryptedMusic' in line:
        print(f"  Found line {i}: {repr(line.strip()[:100])}")
        lines[i] = '                self.output_path.set("G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")'
        print(f"  Fixed to: G:\\QQMusic\\Decrypted\\\\VipSongsDownload")
        break

# Fix 2: Line 56-58 - Directory structure preservation
print("\nFix 2: Directory structure preservation")
for i, line in enumerate(lines):
    if i == 56 and 'output_file_path = os.path.join(output_dir, output_file)' in line:
        print(f"  Found line {i}: {repr(line.strip()[:100])}")
        # Comment out old line
        lines[i] = '                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE\n'
        # Insert new logic BEFORE line 57
        lines.insert(i+1, '                # Preserve directory structure\n')
        lines.insert(i+2, '                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
        lines.insert(i+3, '                output_file_path = os.path.join(output_dir, relative_path)\n')
        print(f"  Fixed lines {i}-{i+3}")
        break

# Write back
print("\nWriting fixed file...")
with open(gui_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done! Both fixes applied successfully.")
print("\nPlease run GUI to test:")
print("1. Check output directory default: G:\\QQMusic\\Decrypted\\VipSongsDownload")
print("2. Check that files are saved to output directory with correct structure")
