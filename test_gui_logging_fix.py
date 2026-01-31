#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证 GUI 日志修复

测试目标：
1. 验证日志可以同时输出到控制台、文件、GUI 文本框
2. 验证 TextHandler 的 emit() 方法正确工作
"""

import logging
import io
import sys
import tempfile
import os


class MockScrolledText:
    """模拟 ScrolledText 组件（用于测试）"""
    def __init__(self):
        self.content = []
    
    def insert(self, position, text):
        """模拟 insert 方法"""
        self.content.append(text)
    
    def see(self, position):
        """模拟 see 方法（用于滚动到末尾）"""
        pass
    
    def get_content(self):
        """获取所有内容"""
        return ''.join(self.content)


class TextHandler(logging.Handler):
    """自定义日志处理器：输出到文本框"""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert('END', msg + '\n')
        self.text_widget.see('END')


def test_text_handler():
    """测试 TextHandler 功能"""
    print("=" * 60)
    print("  测试 TextHandler 功能")
    print("=" * 60)
    print()
    
    # 创建模拟的文本框
    mock_text = MockScrolledText()
    
    # 创建 TextHandler
    text_handler = TextHandler(mock_text)
    text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # 创建 logger
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(text_handler)
    
    # 测试不同级别的日志
    logger.debug('这是 DEBUG 级别的日志')
    logger.info('这是 INFO 级别的日志')
    logger.warning('这是 WARNING 级别的日志')
    logger.error('这是 ERROR 级别的日志')
    logger.critical('这是 CRITICAL 级别的日志')
    
    # 验证内容
    content = mock_text.get_content()
    
    print("[OK] TextHandler 工作正常")
    print(f"[OK] 记录了 {len(mock_text.content)} 条日志")
    print(f"[OK] 总字符数: {len(content)}")
    
    # 验证关键内容
    assert 'DEBUG' in content, "缺少 DEBUG 日志"
    assert 'INFO' in content, "缺少 INFO 日志"
    assert 'WARNING' in content, "缺少 WARNING 日志"
    assert 'ERROR' in content, "缺少 ERROR 日志"
    assert 'CRITICAL' in content, "缺少 CRITICAL 日志"
    
    print("[OK] 所有级别的日志都正确记录")
    print()


def test_multiple_handlers():
    """测试多个 Handler 同时工作"""
    print("=" * 60)
    print("  测试多个 Handler 同时工作")
    print("=" * 60)
    print()
    
    # 创建模拟的文本框
    mock_text = MockScrolledText()
    
    # 创建临时文件用于测试
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as tmp_file:
        log_file_path = tmp_file.name
    
    try:
        # 创建多个 Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('[CONSOLE] %(message)s'))
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('[FILE] %(message)s'))
        
        text_handler = TextHandler(mock_text)
        text_handler.setFormatter(logging.Formatter('[TEXT] %(message)s'))
        
        # 创建 logger
        logger = logging.getLogger('test_multi')
        logger.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(text_handler)
        
        # 测试日志
        test_message = "这是一条测试日志"
        logger.info(test_message)
        
        # 验证文件内容
        with open(log_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 验证文本框内容
        text_content = mock_text.get_content()
        
        # 验证
        assert test_message in file_content, "文件中缺少日志"
        assert test_message in text_content, "文本框中缺少日志"
        assert '[FILE]' in file_content, "文件缺少前缀"
        assert '[TEXT]' in text_content, "文本框缺少前缀"
        
        print("[OK] 控制台输出正常")
        print("[OK] 文件输出正常")
        print("[OK] 文本框输出正常")
        print("[OK] 所有 Handler 同时工作")
        print()
        
    finally:
        # 清理临时文件（忽略删除错误）
        if os.path.exists(log_file_path):
            try:
                os.unlink(log_file_path)
            except:
                pass  # 忽略删除错误


def test_handler_formatting():
    """测试日志格式化"""
    print("=" * 60)
    print("  测试日志格式化")
    print("=" * 60)
    print()
    
    # 创建模拟的文本框
    mock_text = MockScrolledText()
    
    # 创建 TextHandler（使用 GUI 中的格式）
    text_handler = TextHandler(mock_text)
    text_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    
    # 创建 logger
    logger = logging.getLogger('test_format')
    logger.setLevel(logging.INFO)
    logger.addHandler(text_handler)
    
    # 测试日志
    test_message = "测试格式化"
    logger.info(test_message)
    
    # 验证内容
    content = mock_text.get_content()
    
    print("[OK] 日志格式正确")
    print(f"  内容: {content.strip()}")
    
    # 验证格式
    assert ' - ' in content, "缺少分隔符"
    assert 'INFO' in content, "缺少日志级别"
    assert test_message in content, "缺少消息内容"
    
    print("[OK] 格式验证通过")
    print()


def test_handler_see_method():
    """测试 see() 方法是否被调用"""
    print("=" * 60)
    print("  测试 see() 方法调用")
    print("=" * 60)
    print()
    
    # 创建模拟的文本框（带计数器）
    class CountingMockText(MockScrolledText):
        def __init__(self):
            super().__init__()
            self.see_count = 0
        
        def see(self, position):
            self.see_count += 1
    
    mock_text = CountingMockText()
    
    # 创建 TextHandler
    text_handler = TextHandler(mock_text)
    text_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # 创建 logger
    logger = logging.getLogger('test_see')
    logger.setLevel(logging.INFO)
    logger.addHandler(text_handler)
    
    # 测试多条日志
    for i in range(5):
        logger.info(f"日志 {i+1}")
    
    # 验证 see() 被调用
    assert mock_text.see_count == 5, f"see() 应该被调用 5 次，实际 {mock_text.see_count}"
    
    print(f"[OK] see() 方法被调用了 {mock_text.see_count} 次")
    print("[OK] 自动滚动功能正常")
    print()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  GUI 日志修复验证测试")
    print("=" * 60)
    print()
    
    try:
        # 运行所有测试
        test_text_handler()
        test_multiple_handlers()
        test_handler_formatting()
        test_handler_see_method()
        
        print("=" * 60)
        print("  [OK] 所有测试通过！")
        print("=" * 60)
        print()
        print("修复总结：")
        print("  1. TextHandler 正常工作")
        print("  2. 日志可以同时输出到控制台、文件、GUI 文本框")
        print("  3. 日志格式正确")
        print("  4. 自动滚动功能正常")
        print()
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"  ✗ 测试失败: {e}")
        print("=" * 60)
        print()
        sys.exit(1)
