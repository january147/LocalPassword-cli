#!/bin/bash
# 密码管理器 GUI 启动脚本 - CLI 版本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 密码管理器可执行文件路径
PM_BIN="$SCRIPT_DIR/target/release/pm"

# GUI 脚本路径（使用 CLI 版本）
GUI_SCRIPT="$SCRIPT_DIR/gui/password_manager_gui_cli.py"

# 检查密码管理器是否存在
if [ ! -f "$PM_BIN" ]; then
    echo "错误: 找不到密码管理器可执行文件"
    echo "请先编译密码管理器: cargo build --release"
    exit 1
fi

# 检查 GUI 脚本是否存在
if [ ! -f "$GUI_SCRIPT" ]; then
    echo "错误: 找不到 GUI 脚本"
    exit 1
fi

# 确保 pm 可执行
chmod +x "$PM_BIN"

# 运行 GUI
cd "$SCRIPT_DIR"
python3 "$GUI_SCRIPT"
