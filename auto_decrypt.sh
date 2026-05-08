#!/bin/bash
# QQ Music 解密工具 - 自动解密脚本
# Git Bash 版本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  QQ Music 批量解密工具"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "[错误] Python 未安装"
    exit 1
fi

echo "[OK] 找到 Python: $(python --version)"

# 检查 CLI 文件
CLI_FILE="src/main_cli.py"
if [ ! -f "$CLI_FILE" ]; then
    echo "[错误] 找不到 $CLI_FILE"
    exit 1
fi

echo "[OK] 找到 CLI 文件"
echo ""

# 运行解密
echo "开始解密..."
echo ""
python "$CLI_FILE" "$@"

echo ""
echo "========================================"
echo "  解密完成！"
echo "========================================"
echo ""
echo "日志文件: logs/decrypt.log"
echo "统计信息: logs/stats.json"
echo ""
