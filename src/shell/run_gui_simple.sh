#!/bin/bash

# 启动 GUI 的脚本（Git Bash 版本）
# 相当于 run_gui_simple.bat 的功能

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}/../.."

echo "启动 GUI..."
echo "脚本目录: $SCRIPT_DIR"
echo ""

# 运行 GUI 程序
python src/gui/main_gui.py

# 检查执行结果
if [ $? -ne 0 ]; then
    echo ""
    echo "发生错误，按任意键退出..."
    read -n 1 -s
    exit 1
fi

echo ""
echo "GUI 已启动"
echo ""
