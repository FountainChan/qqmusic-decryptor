#!/bin/bash
# 环境检查脚本 - Git Bash 版本
# 检查解密工具所需的依赖和服务

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../.."

echo "========================================"
echo "  QQ Music 解密工具 - 环境检查"
echo "========================================"
echo ""

# 检查计数
PASS=0
FAIL=0

# 1. 检查 Python
echo "检查 1: Python"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "[OK] $PYTHON_VERSION"
    ((PASS++))
else
    echo "[FAIL] Python 未安装"
    ((FAIL++))
fi
echo ""

# 2. 检查 frida
echo "检查 2: frida"
if python -c "import frida" 2>/dev/null; then
    FRIDA_VERSION=$(python -c "import frida; print(frida.__version__)")
    echo "[OK] frida 已安装: $FRIDA_VERSION"
    ((PASS++))
else
    echo "[FAIL] frida 未安装"
    echo "      运行: pip install frida==16.7.10"
    ((FAIL++))
fi
echo ""

# 3. 检查 mutagen
echo "检查 3: mutagen"
if python -c "from mutagen.flac import FLAC" 2>/dev/null; then
    echo "[OK] mutagen 已安装"
    ((PASS++))
else
    echo "[FAIL] mutagen 未安装"
    echo "      运行: pip install mutagen"
    ((FAIL++))
fi
echo ""

# 4. 检查 frida-server
echo "检查 4: frida-server"
if command -v frida-ps &> /dev/null; then
    echo "[OK] frida 命令可用"
    if frida-ps &> /dev/null; then
        echo "[OK] frida-server 正在运行"
        ((PASS++))
    else
        echo "[FAIL] frida 无法连接"
        echo "      请确保 QQ Music 正在运行"
        ((FAIL++))
    fi
else
    echo "[FAIL] frida 命令未找到"
    echo "      运行: pip install frida-tools"
    ((FAIL++))
fi
echo ""

# 5. 检查 QQ Music
echo "检查 5: QQ Music"
if tasklist.exe 2>/dev/null | grep -i "QQMusic.exe" &> /dev/null; then
    echo "[OK] QQ Music 正在运行"
    ((PASS++))
else
    echo "[FAIL] QQ Music 未运行"
    echo "      请启动 QQ Music 客户端并登录 VIP"
    ((FAIL++))
fi
echo ""

# 6. 检查目录结构
echo "检查 6: 目录结构"
DIRS_OK=true

if [ ! -d "src/gui" ]; then
    echo "[FAIL] 缺少 src/gui 目录"
    DIRS_OK=false
fi

if [ ! -d "logs" ]; then
    echo "[FAIL] 缺少 logs 目录"
    DIRS_OK=false
fi

if [ ! -f "src/hook_qq_music.js" ]; then
    echo "[FAIL] 缺少 src/hook_qq_music.js"
    DIRS_OK=false
fi

if [ "$DIRS_OK" = true ]; then
    echo "[OK] 目录结构完整"
    ((PASS++))
else
    ((FAIL++))
fi
echo ""

# 7. 检查配置文件
echo "检查 7: 配置文件"
if [ -f "config.ini" ]; then
    echo "[OK] config.ini 存在"
    ((PASS++))
else
    echo "[WARN] config.ini 不存在，将使用默认配置"
fi
echo ""

# 总结
echo "========================================"
echo "  检查结果"
echo "========================================"
echo "通过: $PASS"
echo "失败: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "[OK] 所有检查通过！可以开始使用。"
    echo ""
    echo "启动方式："
    echo "  GUI: bash start_gui.sh"
    echo "  CLI: bash auto_decrypt.sh"
else
    echo "[FAIL] 发现 $FAIL 个问题，请解决后再使用。"
    echo ""
    echo "常见解决方案："
    echo "  1. 安装依赖: pip install -r requirements.txt"
    echo "  2. 启动 QQ Music 并登录 VIP"
    echo "  3. 启动 QQ Music 并登录 VIP"
fi
echo ""

exit $FAIL
