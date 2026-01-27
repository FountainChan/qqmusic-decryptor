import os

gui_file = r"D:\WorkDev\qqmusic_decryptor\gui_backup\main_gui.py"

# Read file
with open(gui_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: Line 99 - Output directory default value
print("Applying Fix 1: Output directory default value")
fix1_applied = False
for i, line in enumerate(lines):
    if i == 98 and i+1 < len(lines):
        # Check if line 99 has the old value
        if 'DecryptedMusic' in line and 'output_path.set' in line:
            lines[i+1] = '                self.output_path.set("G:\\\\QQMusic\\Decrypted\\\\VipSongsDownload")'
            fix1_applied = True
            print(f"  Fixed line {i+1}")
            break

if not fix1_applied:
    print("ERROR: Could not find line 99 to fix output directory")

# Fix 2: Line 56-58 - Directory structure preservation
print("\nApplying Fix 2: Directory structure preservation")
fix2_applied = False
for i, line in enumerate(lines):
    if i == 55 and i+1 < len(lines):
        # Check if line 56 has the old logic
        if 'output_file_path = os.path.join(output_dir, output_file)' in line:
            # Insert new lines BEFORE line 56
            new_lines = lines[:56]
            new_lines.append('                # Preserve directory structure\n')
            new_lines.append('                relative_path = os.path.relpath(encrypted_file, input_dir)\n')
            new_lines.append('                output_file_path = os.path.join(output_dir, relative_path)\n')
            # Comment out old line
            new_lines.append('                # output_file_path = os.path.join(output_dir, output_file)  # OLD CODE\n')
            # Add rest of lines
            new_lines.extend(lines[56:])
            lines = new_lines
            fix2_applied = True
            print(f"  Fixed lines 56-58")
            break

if not fix2_applied:
    print("ERROR: Could not find line 56 to fix directory structure")

# Write back
print("\nWriting fixed file...")
with open(gui_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Done! Applied:")
print(f"  Fix 1: {fix1_applied}")
print(f"  Fix 2: {fix2_applied}")
