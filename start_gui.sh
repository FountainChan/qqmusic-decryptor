#!/bin/bash
# QQ Music 解密工具 - Git Bash 启动脚本
# 用法：直接运行此脚本即可启动 GUI

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  QQ Music 解密工具 - GUI 启动"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "[错误] Python 未安装"
    exit 1
fi

echo "[OK] 找到 Python: $(python --version)"
echo ""

# 检查 GUI 文件
GUI_FILE="src/gui/main_gui.py"
if [ ! -f "$GUI_FILE" ]; then
    echo "[错误] 找不到 $GUI_FILE"
    exit 1
fi

echo "[OK] 找到 GUI 文件"
echo ""
echo "启动 GUI..."
echo ""

# 使用 pythonw 启动（后台运行，不显示控制台窗口）
pythonw "$GUI_FILE" &

echo "GUI 已启动！"
echo ""
echo "提示："
echo "- 确保 QQ Music 已启动并登录 VIP"
echo ""
echo "日志文件: logs/decrypt.log"
