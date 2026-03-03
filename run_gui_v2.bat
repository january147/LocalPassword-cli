@echo off
REM 密码管理器 GUI 启动脚本 - 增强版 (Windows)

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 密码管理器可执行文件路径
set PM_BIN=%SCRIPT_DIR%target\release\pm.exe

REM GUI 脚本路径（使用增强版）
set GUI_SCRIPT=%SCRIPT_DIR%gui\password_manager_gui_v2.py

REM 检查密码管理器是否存在
if not exist "%PM_BIN%" (
    echo 错误: 找不到密码管理器可执行文件
    echo 请先编译密码管理器: cargo build --release
    pause
    exit /b 1
)

REM 检查 GUI 脚本是否存在
if not exist "%GUI_SCRIPT%" (
    echo 错误: 找不到 GUI 脚本
    pause
    exit /b 1
)

REM 运行 GUI
cd /d "%SCRIPT_DIR%"
python "%GUI_SCRIPT%"

pause
