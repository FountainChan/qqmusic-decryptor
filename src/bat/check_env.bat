@echo off
set MISSING=0

echo ========================================
echo   环境检查
echo ========================================
echo.

echo [1/6] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [✗] Python未安装
    set MISSING=1
) else (
    echo [✓] Python已安装
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo     版本: %PYTHON_VERSION%
)
echo.

echo [2/6] 检查frida包...
python -c "import frida" >nul 2>&1
if errorlevel 1 (
    echo [✗] frida包未安装
    echo     运行: pip install -r requirements.txt
    set MISSING=1
) else (
    echo [✓] frida包已安装
    for /f "tokens=*" %%i in ('python -c "import frida; print(frida.__version__)"') do set FRIDA_VERSION=%%i
    echo     版本: %FRIDA_VERSION%
)
echo.

echo [3/6] 检查frida可用...
python -c "import frida; print('OK')" >nul 2>&1
if errorlevel 1 (
    echo [✗] frida未安装
    echo     运行: pip install -r requirements.txt
    set MISSING=1
) else (
    echo [✓] frida已安装
)
echo.

echo [4/5] 检查QQ Music进程...
tasklist /FI "IMAGENAME eq QQMusic.exe" 2>NUL | find /I /N "QQMusic.exe">NUL
if "%ERRORLEVEL%" neq "0" (
    echo [✗] QQ Music未运行
    echo     正在尝试启动...
    start "" "D:\Software\Tencent\QQMusic\QQMusic1951.01.07.35\QQMusic.exe"
    echo     等待5秒...
    timeout /t 5 /nobreak >nul
    tasklist /FI "IMAGENAME eq QQMusic.exe" 2>NUL | find /I /N "QQMusic.exe">NUL
    if "%ERRORLEVEL%" neq "0" (
        echo     启动失败，请手动启动QQ Music
        set MISSING=1
    ) else (
        echo [✓] QQ Music已启动
    )
) else (
    echo [✓] QQ Music正在运行
)
echo.

echo [5/5] 检查输入目录...
if not exist "G:\QQMusic\Download" (
    echo [✗] 输入目录不存在：G:\QQMusic\Download
    set MISSING=1
) else (
    echo [✓] 输入目录存在
)
echo.

REM 输出目录检查 (原编号6)
if not exist "G:\QQMusic\Decrypted" (
    echo     创建输出目录: G:\QQMusic\Decrypted
    mkdir "G:\QQMusic\Decrypted"
    if errorlevel 1 (
        echo [✗] 无法创建输出目录
        set MISSING=1
    ) else (
        echo [✓] 输出目录已创建
    )
) else (
    echo [✓] 输出目录存在
)
echo.

if %MISSING% equ 0 (
    echo ========================================
    echo   [✓] 所有检查通过，可以开始解密！
    echo ========================================
) else (
    echo ========================================
    echo   [✗] 存在问题，请先解决以上错误
    echo ========================================
)
echo.

exit /b %MISSING%
