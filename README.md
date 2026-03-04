# Password Manager

一个安全的密码管理工具，提供命令行界面（CLI）和图形用户界面（GUI）。

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Rust Version](https://img.shields.io/badge/rust-stable-orange.svg)
![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)

## ✨ 特性

- 🔒 **安全加密** - 使用 AES-256-GCM 加密算法
- 🛡️ **强密码生成** - 可自定义的密码生成器
- 🖥️ **跨平台** - 支持 Linux、Windows 和 macOS
- 💻 **双界面** - 提供命令行和图形界面
- 🔍 **快速搜索** - 支持标题、用户名、URL 搜索
- 📦 **轻量级** - 无外部依赖，单文件数据库
- 🔌 **可集成** - 支持 API 调用和 GUI 集成

## 🚀 快速开始

### 安装

#### 从源码编译

```bash
# 克隆仓库
git clone https://github.com/yourusername/password-manager.git
cd password-manager

# 编译 CLI 工具
cargo build --release

# 二进制文件位于 target/release/pm
```

#### 从 Releases 下载

访问 [Releases](https://github.com/yourusername/password-manager/releases) 下载预编译版本。

### 初始化数据库

```bash
pm init
```

系统会提示你设置主密码。

### 添加第一个密码

```bash
# 交互式添加
pm add

# 非交互式添加
pm add --title "GitHub" --username "user@example.com" --generate
```

## 📚 文档

- **[CLI 使用指南](./docs/cli-guide.md)** - 命令行工具详细使用说明
- **[GUI 集成指南](./docs/gui-integration.md)** - 如何将 CLI 集成到 GUI 应用
- **[日志指南](./docs/logging-guide.md)** - 日志功能使用指南
- **[GUI 使用说明](./gui_new/README.md)** - 现代化 GUI 完整使用指南

## 🏗️ 项目结构

```
password-manager/
├── cli/                    # 命令行工具
│   ├── Cargo.toml
│   └── src/
│       └── main.rs
├── core/                   # 核心密码管理库
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── database.rs
│       ├── entry.rs
│       └── password_generator.rs
├── gui_new/                # 现代化图形界面
│   ├── password_manager.py  # GUI 主程序
│   ├── requirements.txt     # Python 依赖
│   └── README.md          # GUI 使用说明
├── docs/                   # 文档
│   ├── cli-guide.md
│   ├── gui-integration.md
│   └── logging-guide.md
├── target/                 # 编译输出
├── .github/
│   └── workflows/
│       └── build.yml      # GitHub Actions
├── run_gui.sh             # GUI 启动脚本 (Linux/Mac)
├── run_gui.bat            # GUI 启动脚本 (Windows)
├── Cargo.toml
├── Cargo.lock
├── .gitignore
├── PROGRESS.md            # 项目进展
└── README.md              # 本文件
```

## 🔧 CLI 命令

### 基本命令

```bash
pm init                    # 初始化数据库
pm add                     # 添加密码
pm list                    # 列出所有密码
pm get <title>             # 获取密码
pm search <query>          # 搜索密码
pm edit <title>            # 编辑密码
pm delete <title>          # 删除密码
```

### 高级命令

```bash
pm generate                # 生成强密码
pm strength <password>     # 检查密码强度
pm export <path>           # 导出数据库
pm import <path>           # 导入数据库
pm shell                   # 交互式 shell
```

### 非交互式模式

```bash
# 使用环境变量
export PM_MASTER_PASSWORD="your_password"
pm list

# 使用命令行参数
pm --master-password "your_password" list

# 非交互式模式
pm --non-interactive --master-password "your_password" list
```

### 日志功能

```bash
# 启用日志
pm --log list

# 指定日志级别
pm --log --log-level debug list

# 使用环境变量
export PM_LOG=1
export PM_LOG_LEVEL=debug
pm list
```

日志级别：`off`, `error`, `warn`, `info`, `debug`, `trace`

详见：[日志指南](./docs/logging-guide.md)

## 🖥️ GUI 使用

### 现代化 GUI

基于 CustomTkinter 的新 GUI，提供现代化的用户体验：

**特性：**
- 🎨 现代化深色主题
- 🔍 实时搜索
- 📋 一键复制密码
- 🔢 内置密码生成器
- 📤 导出/导入支持
- 🧵 多线程异步操作

#### 安装依赖

```bash
pip3 install -r gui_new/requirements.txt
```

或使用虚拟环境（推荐）：
```bash
python3 -m venv gui_new/venv
source gui_new/venv/bin/activate
pip install -r gui_new/requirements.txt
```

#### 启动 GUI

**Linux/Mac:**
```bash
chmod +x run_gui.sh
./run_gui.sh
```

**Windows:**
```bash
run_gui.bat
```

**直接运行:**
```bash
python3 gui_new/password_manager.py
```

详细文档：[GUI 使用说明](./gui_new/README.md)

## 🔐 安全性

### 加密技术

- **算法**: AES-256-GCM
- **密钥派生**: Argon2id
- **数据库加密**: SQLite + AES

### 最佳实践

1. 使用强主密码（至少16位）
2. 定期备份数据库文件
3. 不要共享或泄露主密码
4. 定期更新密码管理器
5. 在导出时避免包含明文密码

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发

### 开发环境设置

```bash
# 安装 Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 安装 Python 依赖
pip3 install -r requirements.txt

# 编译开发版本
cargo build

# 运行测试
cargo test
```

### 构建发布版本

```bash
# Linux/Mac
cargo build --release --target x86_64-unknown-linux-gnu

# Windows
cargo build --release --target x86_64-pc-windows-msvc
```

## 📦 发布

项目使用 GitHub Actions 自动构建和发布：

- Linux (x86_64) 自动构建
- Windows (x86_64) 自动构建
- 标签推送时自动创建 Release

详见 [.github/workflows/build.yml](./.github/workflows/build.yml)

## 🐛 故障排除

### CLI 问题

**问题**: 命令找不到 `pm`
```bash
# 解决方案：添加到 PATH
export PATH="$PATH:/path/to/password-manager/target/release"
```

**问题**: 主密码错误
```
Failed to open database. Check your master password.
```
- 检查主密码是否正确
- 区分大小写
- 检查是否有多余空格

### GUI 问题

**问题**: GUI 界面显示异常
```bash
# 检查 Tkinter
python3 -c "import tkinter; print('OK')"

# Ubuntu/Debian 安装 Tkinter
sudo apt-get install python3-tk
```

**问题**: 找不到 pm 可执行文件
```bash
# 确保 CLI 已编译
cargo build --release
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [clap](https://github.com/clap-rs/clap) - 命令行参数解析
- [rusqlite](https://github.com/rusqlite/rusqlite) - SQLite 绑定
- [argon2](https://github.com/RustCrypto/password-hashes/tree/master/argon2) - 密钥派生
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI 框架

## 📞 联系方式

- **项目主页**: https://github.com/yourusername/password-manager
- **问题反馈**: https://github.com/yourusername/password-manager/issues
- **讨论区**: https://github.com/yourusername/password-manager/discussions

## 🗺️ 路线图

### 已完成 ✅

- [x] 核心密码管理功能
- [x] CLI 界面
- [x] GUI 界面
- [x] 密码生成器
- [x] 搜索功能
- [x] 导入/导出
- [x] GitHub Actions CI/CD
- [x] 非交互式模式支持

### 进行中 🔄

- [ ] 浏览器扩展
- [ ] 云同步功能
- [ ] 移动端应用

### 计划中 📋

- [ ] 两步验证 (2FA)
- [ ] 密码分享功能
- [ ] 安全审计功能
- [ ] 密码过期提醒
- [ ] 多用户支持

---

**享受安全的密码管理体验！** 🔐
