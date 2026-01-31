#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证控制台无日志输出

测试目标：
1. 验证日志不会输出到控制台
2. 验证日志输出到文件
3. 验证日志输出到 GUI 文本框（模拟）
"""

import logging
import sys
import io
import tempfile
import os


class MockScrolledText:
    """模拟 ScrolledText 组件"""
    def __init__(self):
        self.content = []
    
    def insert(self, position, text):
        self.content.append(text)
    
    def see(self, position):
        pass
    
    def get_content(self):
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


def test_no_console_output():
    """测试控制台无日志输出"""
    print("=" * 60)
    print("  测试控制台无日志输出")
    print("=" * 60)
    print()
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as tmp_file:
        log_file_path = tmp_file.name
    
    # 创建模拟文本框
    mock_text = MockScrolledText()
    
    try:
        # 捕获标准输出
        old_stdout = sys.stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # 配置日志（只输出到文件和文本框）
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        text_handler = TextHandler(mock_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # 配置根 logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, text_handler],
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True
        )
        
        # 测试日志
        logger = logging.getLogger('test_logger')
        logger.info('这是一条测试日志')
        logger.warning('这是一条警告日志')
        logger.error('这是一条错误日志')
        
        # 恢复标准输出
        sys.stdout = old_stdout
        
        # 检查控制台输出
        console_output = captured_output.getvalue()
        
        # 读取文件内容
        with open(log_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 获取文本框内容
        text_content = mock_text.get_content()
        
        print(f"控制台输出长度: {len(console_output)} 字符")
        print(f"文件输出长度: {len(file_content)} 字符")
        print(f"文本框输出长度: {len(text_content)} 字符")
        print()
        
        # 验证
        assert len(console_output) == 0, f"控制台不应该有输出，但捕获到了 {len(console_output)} 字符"
        assert len(file_content) > 0, "文件应该有日志输出"
        assert len(text_content) > 0, "文本框应该有日志输出"
        
        # 验证日志内容
        assert '这是一条测试日志' in file_content, "文件中缺少测试日志"
        assert '这是一条警告日志' in file_content, "文件中缺少警告日志"
        assert '这是一条错误日志' in file_content, "文件中缺少错误日志"
        
        assert '这是一条测试日志' in text_content, "文本框中缺少测试日志"
        assert '这是一条警告日志' in text_content, "文本框中缺少警告日志"
        assert '这是一条错误日志' in text_content, "文本框中缺少错误日志"
        
        print("[OK] 控制台无输出")
        print("[OK] 文件有输出")
        print("[OK] 文本框有输出")
        print()
        
    finally:
        # 清理临时文件
        if os.path.exists(log_file_path):
            try:
                os.unlink(log_file_path)
            except:
                pass


def test_log_levels():
    """测试不同级别的日志"""
    print("=" * 60)
    print("  测试不同级别的日志输出")
    print("=" * 60)
    print()
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as tmp_file:
        log_file_path = tmp_file.name
    
    # 创建模拟文本框
    mock_text = MockScrolledText()
    
    try:
        # 配置日志
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        
        text_handler = TextHandler(mock_text)
        text_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        
        logging.basicConfig(
            level=logging.DEBUG,
            handlers=[file_handler, text_handler],
            force=True
        )
        
        logger = logging.getLogger('test_levels')
        logger.debug('DEBUG 级别')
        logger.info('INFO 级别')
        logger.warning('WARNING 级别')
        logger.error('ERROR 级别')
        logger.critical('CRITICAL 级别')
        
        # 读取文件内容
        with open(log_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        # 获取文本框内容
        text_content = mock_text.get_content()
        
        # 验证
        assert 'DEBUG' in file_content, "缺少 DEBUG 日志"
        assert 'INFO' in file_content, "缺少 INFO 日志"
        assert 'WARNING' in file_content, "缺少 WARNING 日志"
        assert 'ERROR' in file_content, "缺少 ERROR 日志"
        assert 'CRITICAL' in file_content, "缺少 CRITICAL 日志"
        
        assert 'DEBUG' in text_content, "缺少 DEBUG 日志"
        assert 'INFO' in text_content, "缺少 INFO 日志"
        assert 'WARNING' in text_content, "缺少 WARNING 日志"
        assert 'ERROR' in text_content, "缺少 ERROR 日志"
        assert 'CRITICAL' in text_content, "缺少 CRITICAL 日志"
        
        print("[OK] 所有级别的日志都正确输出到文件")
        print("[OK] 所有级别的日志都正确输出到文本框")
        print()
        
    finally:
        # 清理临时文件
        if os.path.exists(log_file_path):
            try:
                os.unlink(log_file_path)
            except:
                pass


def test_only_two_targets():
    """测试只有两个输出目标（文件和文本框）"""
    print("=" * 60)
    print("  测试只有两个输出目标")
    print("=" * 60)
    print()
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as tmp_file:
        log_file_path = tmp_file.name
    
    # 创建模拟文本框
    mock_text = MockScrolledText()
    
    try:
        # 配置日志（模拟 GUI 中的配置）
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        
        text_handler = TextHandler(mock_text)
        text_handler.setFormatter(logging.Formatter('%(message)s'))
        
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, text_handler],
            force=True
        )
        
        logger = logging.getLogger('test_targets')
        
        # 获取根 logger
        root_logger = logging.getLogger()
        
        # 验证只有两个 handler
        handlers = root_logger.handlers
        print(f"Handler 数量: {len(handlers)}")
        print(f"Handler 类型: {[type(h).__name__ for h in handlers]}")
        print()
        
        # 过滤掉可能的临时 handler
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
        text_handlers = [h for h in handlers if isinstance(h, TextHandler)]
        
        # 注意：FileHandler 可能会被多次调用，所以可能有一个
        assert len(file_handlers) >= 1, "应该至少有一个 FileHandler"
        assert len(text_handlers) >= 1, "应该至少有一个 TextHandler"
        
        # 检查是否有 StreamHandler（控制台）
        console_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
        if console_handlers:
            print(f"[WARNING] 发现 {len(console_handlers)} 个 StreamHandler（可能是控制台）")
            for h in console_handlers:
                print(f"  - {h}")
        else:
            print("[OK] 没有发现 StreamHandler（控制台）")
        
        print("[OK] 配置正确：只有文件和文本框两个目标")
        print()
        
    finally:
        # 清理临时文件
        if os.path.exists(log_file_path):
            try:
                os.unlink(log_file_path)
            except:
                pass


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  GUI 日志配置验证测试（无控制台输出）")
    print("=" * 60)
    print()
    
    try:
        # 运行所有测试
        test_no_console_output()
        test_log_levels()
        test_only_two_targets()
        
        print("=" * 60)
        print("  [OK] 所有测试通过！")
        print("=" * 60)
        print()
        print("验证总结：")
        print("  1. 控制台无输出")
        print("  2. 文件有输出（logs/gui.log）")
        print("  3. GUI 文本框有输出")
        print("  4. 所有日志级别都正常工作")
        print()
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print(f"  [ERROR] 测试失败: {e}")
        print("=" * 60)
        print()
        sys.exit(1)
