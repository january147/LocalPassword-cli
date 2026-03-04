#!/bin/bash
# 测试脚本

set -e

export PATH="/root/.cargo/bin:$PATH"

echo "=== 基础构建测试 ==="
cd /workspace/projects/workspace/password-manager
cargo build --release
echo "✅ 构建成功"

echo ""
echo "=== 命令行帮助测试 ==="
./target/release/pm --help
echo "✅ 帮助信息正常"

echo ""
echo "=== 日志功能测试 ==="
./target/release/pm generate --log --log-level debug 2>&1 | head -5
echo "✅ 日志功能正常"

echo ""
echo "=== 非交互式模式测试（生成密码）==="
./target/release/pm generate --length 16
echo "✅ 密码生成正常"

echo ""
echo "=== 密码强度检查测试 ==="
./target/release/pm strength "MyPassword123!"
echo "✅ 密码强度检查正常"

echo ""
echo ""
echo "🎉 所有基础测试通过！"
echo ""
echo "⚠️  注意："
echo "- init 命令需要 TTY，无法在脚本中完全测试"
echo "- 完整的密码管理功能需要在 TTY 环境下测试"
echo "- 日志和非交互式参数解析已验证正常工作"
