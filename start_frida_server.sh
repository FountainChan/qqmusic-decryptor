#!/bin/bash
# Frida Server 启动脚本 - Git Bash 版本
# 注意：需要管理员权限，请在 Git Bash 中以管理员身份运行

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Frida Server 启动脚本"
echo "========================================"
echo ""

# 检查 frida-server 是否存在
if [ ! -f "frida-server.exe" ]; then
    echo "[错误] 未找到 frida-server.exe"
    echo ""
    echo "请按以下步骤下载和安装 frida-server："
    echo "1. 访问: https://github.com/frida/frida/releases"
    echo "2. 下载: frida-server-16.7.10-windows-x86_64.exe.xz"
    echo "3. 解压后放到当前目录"
    echo "4. 重命名为: frida-server.exe"
    echo ""
    exit 1
fi

echo "[OK] 找到 frida-server.exe"
echo ""
echo "启动 frida-server..."
echo ""
echo "========================================"
echo "  重要提示："
echo "  1. 请不要关闭此窗口！"
echo "  2. 此窗口必须保持打开状态！"
echo "  3. 完成解密后可以关闭"
echo "========================================"
echo ""

# 启动 frida-server
./frida-server.exe

echo ""
echo "Frida Server 已停止"
