# Password Manager CLI 使用指南

## 概述

Password Manager CLI (`pm`) 是一个安全的命令行密码管理工具，支持密码的存储、检索、生成和管理。

## 安装

### 从源码编译

```bash
# 克隆仓库
git clone https://github.com/yourusername/password-manager.git
cd password-manager

# 编译
cargo build --release

# 二进制文件位于 target/release/pm
```

### 从 GitHub Releases 下载

访问 [Releases](https://github.com/yourusername/password-manager/releases) 页面下载适合你系统的预编译二进制文件。

- Linux: `pm-linux-x86_64`
- Windows: `pm-windows-x86_64.exe`

## 初始化

### 创建新数据库

```bash
pm init
```

系统会提示你设置主密码：

```
Set master password: *****
Confirm master password: *****
```

**⚠️ 重要提示：** 主密码无法恢复，请妥善保存！

### 指定数据库位置

```bash
pm init --db /path/to/passwords.db
```

默认数据库位置：`~/.pm.db`

## 使用指南

### 认证方式

#### 1. 交互式输入（默认）

```bash
pm list
# 系统会提示输入主密码
Enter master password: *****
```

#### 2. 命令行参数（非交互式）

```bash
pm --master-password "your_password" list
```

#### 3. 环境变量（推荐用于脚本）

```bash
export PM_MASTER_PASSWORD="your_password"
pm list
```

#### 4. 非交互式模式

```bash
pm --non-interactive --master-password "your_password" list
```

在非交互式模式下，如果缺少必需参数会报错而不是提示输入。

### 基本命令

#### 添加密码条目

```bash
# 交互式添加（推荐）
pm add

# 非交互式添加
pm add --title "GitHub" --username "user@example.com" --password "MySecurePassword"

# 自动生成密码
pm add --title "Netflix" --username "user@example.com" --generate 20

# 生成密码并复制到剪贴板
pm add --title "Bank" --username "user@example.com" --generate --copy
```

#### 列出所有密码

```bash
# 列出所有（不显示密码）
pm list

# 显示明文密码（危险！）
pm list --show-passwords

# 按类别过滤
pm list --category "work"

# 搜索
pm list --search "github"
```

#### 获取特定密码

```bash
# 按标题获取
pm get GitHub

# 按ID获取
pm get 1

# 显示密码
pm get GitHub --show-password

# 复制到剪贴板
pm get GitHub --copy
```

#### 搜索密码

```bash
# 按标题搜索（默认）
pm search "github"

# 按用户名搜索
pm search "user@example.com" --username

# 按URL搜索
pm search "github.com" --url

# 按类别搜索
pm search "work" --category
```

#### 编辑密码

```bash
pm edit GitHub
```

#### 删除密码

```bash
# 删除（需要确认）
pm delete GitHub

# 强制删除（无需确认）
pm delete GitHub --force
```

### 高级功能

#### 生成强密码

```bash
# 生成20位密码（默认）
pm generate

# 指定长度
pm generate --length 32

# 自定义字符集
pm generate --length 16 --uppercase --lowercase --numbers --symbols

# 生成并复制
pm generate --copy
```

#### 检查密码强度

```bash
pm strength "MyPassword123"
```

#### 导出数据库

```bash
# 导出（不包含密码）
pm export backup.json

# 导出包含密码（危险！）
pm export backup.json --include-passwords
```

#### 导入数据库

```bash
pm import backup.json
```

### 交互式 Shell 模式

进入交互式 shell 后，可以连续执行多个命令而无需重复输入主密码：

```bash
pm shell
```

在 shell 内可用的命令：

- `list` - 列出所有密码
- `add` - 添加新密码
- `get <title/id>` - 获取密码详情
- `search <query>` - 搜索密码
- `edit <title/id>` - 编辑密码
- `delete <title/id>` - 删除密码
- `generate [len]` - 生成强密码
- `strength <pwd>` - 检查密码强度
- `help` - 显示帮助
- `exit` - 退出 shell

## 与 GUI 工具集成

### Python 集成示例

```python
import subprocess
import os
import json

def get_password(title, master_password):
    """获取指定标题的密码"""
    env = os.environ.copy()
    env['PM_MASTER_PASSWORD'] = master_password

    result = subprocess.run(
        ['pm', '--non-interactive', 'get', title, '--show-password'],
        capture_output=True,
        text=True,
        env=env
    )

    # 解析输出获取密码
    # ... 解析逻辑

    return password

def list_passwords(master_password):
    """列出所有密码"""
    env = os.environ.copy()
    env['PM_MASTER_PASSWORD'] = master_password

    result = subprocess.run(
        ['pm', '--non-interactive', 'list', '--show-passwords'],
        capture_output=True,
        text=True,
        env=env
    )

    # 解析输出
    # ... 解析逻辑

    return entries
```

### Node.js 集成示例

```javascript
const { execSync } = require('child_process');
const os = require('os');

function getMasterPassword() {
  // 从安全存储获取主密码
  return process.env.PM_MASTER_PASSWORD;
}

function getPassword(title) {
  const env = {
    ...process.env,
    PM_MASTER_PASSWORD: getMasterPassword()
  };

  const output = execSync(
    `pm --non-interactive get "${title}" --show-password`,
    { env, encoding: 'utf8' }
  );

  // 解析输出
  // ... 解析逻辑

  return password;
}
```

## 安全最佳实践

1. **主密码安全**
   - 使用强主密码（至少16位，包含大小写字母、数字和符号）
   - 不要使用常见密码或个人信息
   - 定期更换主密码（但需要重新加密数据库）

2. **环境变量**
   - 避免在 shell 历史中记录主密码
   - 使用 `export PM_MASTER_PASSWORD="your_password"` 时，历史会记录
   - 更安全的方式：使用密钥管理工具或交互式输入

3. **数据库文件**
   - 将数据库文件存储在加密位置
   - 定期备份数据库文件
   - 在导出时避免包含明文密码

4. **命令行参数**
   - 命令行参数可能被进程监控工具看到
   - 敏感环境推荐使用环境变量或交互式输入

## 故障排除

### 主密码错误

```
Failed to open database. Check your master password.
```

解决方法：
- 确认主密码正确
- 主密码区分大小写
- 检查是否输入了多余空格

### 数据库已存在

```
Database already exists at /path/to/.pm.db. Overwrite? [y/N]
```

解决方法：
- 输入 `y` 覆盖现有数据库（会丢失所有数据）
- 输入 `N` 取消操作
- 使用不同的数据库路径：`pm init --db /path/to/new.db`

### 权限问题

```
Permission denied (os error 13)
```

解决方法：
- 检查数据库文件权限
- 确保有读写权限
- 使用 `chmod` 修改权限

## 完整命令参考

```bash
pm [OPTIONS] <COMMAND>

OPTIONS:
    -d, --db <FILE>          数据库路径（默认: ~/.pm.db）
        --master-password <PASSWORD>
                            主密码（或使用 PM_MASTER_PASSWORD 环境变量）
        --non-interactive   非交互式模式
    -h, --help               显示帮助信息
    -V, --version            显示版本信息

COMMANDS:
    init                     初始化新数据库
    add                      添加密码条目
    list                     列出所有密码
    get <title>              获取密码详情
    search <query>           搜索密码
    edit <title>             编辑密码
    delete <title>           删除密码
    generate                 生成强密码
    strength <password>      检查密码强度
    export <path>            导出数据库
    import <path>            导入数据库
    shell                    进入交互式 shell
```

## 示例工作流

### 第一次使用

```bash
# 1. 初始化数据库
pm init

# 2. 添加第一个密码
pm add

# 3. 测试查看
pm list

# 4. 测试搜索
pm search "github"
```

### 日常使用

```bash
# 设置环境变量（推荐）
export PM_MASTER_PASSWORD="your_password"

# 查看所有密码
pm list

# 搜索密码
pm search "work"

# 获取特定密码
pm get "GitHub"

# 添加新密码
pm add --title "New Service" --username "user@example.com" --generate

# 生成新密码
pm generate --length 24
```

## 相关文档

- [GUI 集成指南](./gui-integration.md)
- [项目主页](https://github.com/yourusername/password-manager)
- [问题反馈](https://github.com/yourusername/password-manager/issues)
