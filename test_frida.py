#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Frida测试脚本 - 验证frida-server和脚本是否正常工作
"""

import frida
import time

print("开始测试Frida...")

# 连接到QQ Music
try:
    session = frida.attach("QQMusic.exe")
    print("✓ 成功连接到QQ Music进程")
except Exception as e:
    print(f"✗ 连接失败: {e}")
    exit(1)

# 创建简单的测试脚本
test_script = """
rpc.exports = {
    test: function() {
        console.log("[TEST] Test function called");
        return "OK";
    }
};

console.log("[INFO] Test script loaded");
"""

try:
    script = session.create_script(test_script)
    script.load()
    print("✓ 测试脚本加载成功")
except Exception as e:
    print(f"✗ 脚本加载失败: {e}")
    exit(1)

# 等待脚本加载
time.sleep(1)

# 测试调用
try:
    result = script.exports.test()
    print(f"✓ 测试调用成功: {result}")
except Exception as e:
    print(f"✗ 测试调用失败: {e}")
    print(f"   错误类型: {type(e)}")
    exit(1)

# 断开连接
session.detach()
print("\n✓ Frida测试完成！")
