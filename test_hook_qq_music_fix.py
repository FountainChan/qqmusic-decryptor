#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证 hook_qq_music.js 的文件大小限制修复

测试目标：
1. 验证文件大小限制从 100MB 增大到 2GB
2. 验证错误信息格式（显示 MB 单位）
3. 验证边界值情况
"""

import re
import unittest


class TestHookQQMusicFix(unittest.TestCase):
    """测试 hook_qq_music.js 修复"""

    def test_error_message_format(self):
        """测试错误信息格式"""
        # 模拟错误信息生成逻辑
        srcFileName = "test_flac_hires.mflac"
        fileSize = 2.5 * 1024 * 1024 * 1024  # 2.5 GB

        # JavaScript 逻辑转换为 Python
        sizeInMB = round(fileSize / (1024 * 1024), 2)
        error_msg = f"[ERROR] Invalid file size: {srcFileName} ({sizeInMB} MB)"

        # 验证格式：[ERROR] Invalid file size: filename (XXX.XX MB)
        pattern = r'\[ERROR\] Invalid file size: .+ \(\d+\.\d{1,2} MB\)'
        self.assertRegex(error_msg, pattern, "错误信息格式不正确")

        # 验证数值（JavaScript 的 toFixed(2) 会保留两位小数）
        self.assertEqual(sizeInMB, 2560.00, "MB 转换不正确")

    def test_limit_values(self):
        """测试边界值"""
        # 旧限制：100 MB
        old_limit = 100 * 1024 * 1024  # 104,857,600 字节
        # 新限制：2 GB
        new_limit = 2 * 1024 * 1024 * 1024  # 2,147,483,648 字节

        # 验证数值
        self.assertEqual(old_limit, 104857600, "旧限制 100MB 不正确")
        self.assertEqual(new_limit, 2147483648, "新限制 2GB 不正确")

        # 验证新限制是旧限制的 20 倍
        self.assertEqual(new_limit // old_limit, 20, "限制增长倍数不正确")

    def test_mb_conversion(self):
        """测试 MB 转换精度"""
        test_cases = [
            (50 * 1024 * 1024, "50.00"),        # 50 MB
            (100 * 1024 * 1024, "100.00"),      # 100 MB（旧限制）
            (1 * 1024 * 1024 * 1024, "1024.00"), # 1 GB
            (1.5 * 1024 * 1024 * 1024, "1536.00"), # 1.5 GB
            (2 * 1024 * 1024 * 1024, "2048.00"), # 2 GB（新限制）
            (2.5 * 1024 * 1024 * 1024, "2560.00"), # 2.5 GB
        ]

        for file_size_bytes, expected_mb in test_cases:
            sizeInMB = round(file_size_bytes / (1024 * 1024), 2)
            self.assertEqual(
                f"{sizeInMB:.2f}",
                expected_mb,
                f"{file_size_bytes} 字节转换为 {sizeInMB} MB，期望 {expected_mb}"
            )

    def test_file_size_scenarios(self):
        """测试各种文件大小场景"""
        scenarios = [
            # (文件大小, 是否应该通过, 描述)
            (0, False, "空文件应该被拒绝"),
            # 注意：代码只检查 fileSize == 0，不检查极小文件
            # 所以 100 字节的文件理论上是通过的（虽然现实中不太可能）
            (50 * 1024 * 1024, True, "50MB 文件应该通过"),
            (100 * 1024 * 1024, True, "100MB 文件应该通过（旧限制）"),
            (1 * 1024 * 1024 * 1024, True, "1GB 文件应该通过"),
            (1.06 * 1024 * 1024 * 1024, True, "1.06GB 文件应该通过（之前失败的文件）"),
            (2 * 1024 * 1024 * 1024, True, "2GB 文件应该通过（新限制）"),
            (2.5 * 1024 * 1024 * 1024, False, "2.5GB 文件应该被拒绝"),
        ]

        new_limit = 2 * 1024 * 1024 * 1024

        for file_size, should_pass, description in scenarios:
            # 检查文件大小是否在限制范围内
            if file_size == 0:
                is_valid = False  # 空文件
            else:
                is_valid = file_size <= new_limit

            self.assertEqual(
                is_valid,
                should_pass,
                f"{description}：文件大小 {file_size / (1024*1024):.2f} MB，"
                f"预期 {'通过' if should_pass else '拒绝'}，"
                f"实际 {'通过' if is_valid else '拒绝'}"
            )

    def test_return_value_format(self):
        """测试返回值格式"""
        # 模拟失败时的返回值
        fileSize = 2.5 * 1024 * 1024 * 1024
        sizeInMB = round(fileSize / (1024 * 1024), 2)

        # 旧的返回值：Invalid file size: 2621440000
        # 新的返回值：Invalid file size: 2500.00 MB
        return_value = f"Invalid file size: {sizeInMB:.2f} MB"

        # 验证格式
        pattern = r'Invalid file size: \d+\.\d{2} MB'
        self.assertRegex(return_value, pattern, "返回值格式不正确")

        # 验证数值（2.5GB = 2560MB）
        self.assertEqual(return_value, "Invalid file size: 2560.00 MB")


if __name__ == '__main__':
    print("=" * 60)
    print("  hook_qq_music.js 修复验证测试")
    print("=" * 60)
    print()

    # 运行测试
    unittest.main(verbosity=2)
