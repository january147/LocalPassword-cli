# PM CLI 非交互式模式说明

## 🚀 快速开始

从 v0.1.0 开始，PM CLI 提供了两种方式进入**非交互式模式**：

1. **命令行标志**：`--non-interactive`
2. **环境变量**：`PM_NON_INTERACTIVE=1`

在非交互式模式下，PM CLI 不会弹出任何交互式提示。如果缺少必需参数，命令会直接返回错误，而不是等待用户输入。

## 📋 使用场景

### GUI 应用集成

```bash
# JavaScript / Node.js
const { spawn } = require('child_process');

const env = {
  ...process.env,
  PM_MASTER_PASSWORD: masterPassword,
  PM_NON_INTERACTIVE: '1'  // 启用非交互模式
};

const args = [
  'add',
  '--title', title,
  '--username', username,
  '--password', password,
];

spawn('pm', args, { env });
```

### 自动化脚本

```bash
#!/bin/bash
export PM_MASTER_PASSWORD="$(get-password-from-keyring)"
export PM_NON_INTERACTIVE=1

# 添加密码
pm add --title "GitHub" --username "user" --password "pwd123"

# 删除密码（无需 --force，因为非交互模式下不允许交互）
pm delete "GitHub" --force

# 列出密码
pm list
```

### CI/CD 管道

```yaml
# GitHub Actions 示例
- name: Add password
  env:
    PM_MASTER_PASSWORD: ${{ secrets.MASTER_PASSWORD }}
    PM_NON_INTERACTIVE: "1"
  run: |
    pm add --title "Database" --username "admin" --password "${{ secrets.DB_PASSWORD }}"
```

## 🔧 命令详解

### 初始化数据库

```bash
# 交互式模式（默认）
pm init
# 如果数据库已存在，会提示是否覆盖

# 非交互式模式
pm --non-interactive init
# 如果数据库已存在，会报错

# 非交互式模式 + 强制覆盖
pm --non-interactive init --force
# 无提示直接覆盖
```

### 添加密码

```bash
# 交互式模式 - 缺少参数时提示输入
pm add --title "GitHub"
# 提示: Username: [输入]
# 提示: Generate a strong password? [Y/n]: [选择]

# 非交互式模式 - 缺少参数时报错
pm --non-interactive add --title "GitHub"
# Error: Missing required parameter: --username is required in non-interactive mode

# 非交互式模式 - 提供所有参数
pm --non-interactive add \
  --title "GitHub" \
  --username "user@example.com" \
  --password "MyPassword123!"

# 使用自动生成
pm --non-interactive add \
  --title "GitHub" \
  --username "user@example.com" \
  --generate 20
```

**必需参数**（非交互模式）：
- `--title` - 条目标题
- `--username` - 用户名
- `--password` 或 `--generate` - 密码或生成长度

**可选参数**（不提供时使用默认值）：
- `--url` - URL（默认：None）
- `--category` - 分类（默认：None）
- `--notes` - 备注（默认：None）

### 列出密码

```bash
# 交互式模式 - 可能提示输入主密码
pm list

# 非交互式模式 - 必须提供主密码
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive list

# 按类别过滤
pm --non-interactive list --category "Development"

# 搜索
pm --non-interactive list --search "GitHub"
```

### 获取密码

```bash
# 交互式模式
pm get "GitHub"

# 非交互式模式
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive get "GitHub"

# 复制到剪贴板
pm --non-interactive get "GitHub" --copy
```

### 搜索密码

```bash
# 交互式模式
pm search "github"

# 非交互式模式
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive search "github"

# 按用户名搜索
pm --non-interactive search "user@example.com" --username

# 按URL搜索
pm --non-interactive search "github.com" --url

# 按分类搜索
pm --non-interactive search "Dev" --category
```

### 编辑密码

```bash
# ⚠️ 注意：Edit 命令需要交互式模式

# 交互式模式
pm edit "GitHub"
# 提示: Title [GitHub]: [修改或保持]

# 非交互式模式 - 不支持
pm --non-interactive edit "GitHub"
# Error: Edit command requires interactive mode. Use shell mode or interactive CLI for editing.
```

**原因**：编辑命令需要用户提供新值或选择保持原值，不适合非交互式模式。

### 删除密码

```bash
# 交互式模式 - 确认删除
pm delete "GitHub"
# 提示: Are you sure you want to delete this entry? [y/N]: [确认]

# 非交互式模式 - 必须使用 --force
pm --non-interactive delete "GitHub" --force

# 非交互式模式 - 缺少 --force 报错
pm --non-interactive delete "GitHub"
# Error: Delete requires --force flag in non-interactive mode to skip confirmation.
```

### 生成密码

```bash
# 交互式模式
pm generate --length 20

# 非交互式模式
pm --non-interactive generate --length 20

# 不需要数据库访问
```

### 检查密码强度

```bash
# 交互式模式
pm strength "MyPassword123!"

# 非交互式模式
pm --non-interactive strength "MyPassword123!"

# 不需要数据库访问
```

### 导出数据库

```bash
# 交互式模式 - 可能提示输入主密码
pm export backup.json

# 非交互式模式 - 必须提供主密码
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive export backup.json

# 导出包含密码
pm --non-interactive export backup.json --include-passwords
```

### 导入数据库

```bash
# 交互式模式 - 可能提示输入主密码
pm import backup.json

# 非交互式模式 - 必须提供主密码
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive import backup.json
```

### 交互式 Shell

```bash
# ⚠️ 注意：Shell 模式与非交互模式不兼容

# 交互式模式
pm shell
# 进入交互式 shell

# 非交互式模式 - 不支持
pm --non-interactive shell
# Error: Shell mode cannot be used with --non-interactive flag. Shell mode is inherently interactive.
```

## 🎯 主密码传递方式

### 方式一：环境变量（推荐）

```bash
export PM_MASTER_PASSWORD="your-master-password"
pm --non-interactive add --title "GitHub" --username "user" --password "pwd123"
```

### 方式二：命令行参数（不推荐）

```bash
pm --non-interactive \
  --master-password "your-master-password" \
  add --title "GitHub" --username "user" --password "pwd123"
```

**⚠️ 注意**：命令行方式不推荐，因为密码会出现在进程列表和命令历史中。

### 方式三：在子 shell 中设置（最安全）

```bash
(PM_MASTER_PASSWORD="$(get-password)" pm --non-interactive list)
```

## 📊 命令对比表

| 命令 | 交互模式 | 非交互模式 | 特殊要求 |
|------|---------|-----------|---------|
| `init` | ✅ 提示覆盖 | ✅ `--force` 强制 | 非交互模式需要 `--force` 跳过确认 |
| `add` | ✅ 提示缺失参数 | ✅ 必需 `--title`, `--username`, `--password`/`--generate` | 可选参数：`--url`, `--category`, `--notes` |
| `list` | ✅ | ✅ | 需要主密码 |
| `get` | ✅ | ✅ | 需要主密码 |
| `search` | ✅ | ✅ | 需要主密码 |
| `edit` | ✅ | ❌ 不支持 | 交互式操作 |
| `delete` | ✅ 确认删除 | ✅ 必需 `--force` | 跳过确认 |
| `generate` | ✅ | ✅ | 不需要数据库 |
| `strength` | ✅ | ✅ | 不需要数据库 |
| `export` | ✅ | ✅ | 需要主密码 |
| `import` | ✅ | ✅ | 需要主密码 |
| `shell` | ✅ | ❌ 不支持 | 完全交互式 |

## 💡 最佳实践

### 1. GUI 应用集成

```javascript
// ✅ 正确做法
const env = {
  PM_MASTER_PASSWORD: password,
  PM_NON_INTERACTIVE: '1'
};

spawn('pm', ['add', '--title', title, '--username', username, '--password', password], { env });

// ❌ 错误做法 - 会弹出提示
spawn('pm', ['add', '--title', title, '--username', username]);
```

### 2. 自动化脚本

```bash
#!/bin/bash

# ✅ 正确做法 - 非交互模式
export PM_MASTER_PASSWORD="$(pass show pm-master)"
export PM_NON_INTERACTIVE=1

pm add --title "Service" --username "user" --password "$(pass show service/pwd)"
pm delete "Old Entry" --force

# ❌ 错误做法 - 可能卡住等待输入
pm add --title "Service" --username "user"
```

### 3. 安全注意事项

```bash
# ✅ 好的做法 - 子 shell 中设置环境变量
(PM_MASTER_PASSWORD="$(pass show pm)" pm --non-interactive list)

# ❌ 不好的做法 - 密码可能泄露到进程列表
pm --non-interactive --master-password "secret123" list

# ✅ 好的做法 - 使用密钥管理工具
PM_MASTER_PASSWORD="$(aws secretsmanager get-secret-value --secret-id pm-master --query SecretString --output text)" \
  pm --non-interactive list
```

### 4. 错误处理

```python
import subprocess
import json

def add_password(title, username, password, master_password):
    env = {
        'PM_MASTER_PASSWORD': master_password,
        'PM_NON_INTERACTIVE': '1'
    }

    result = subprocess.run(
        ['pm', 'add', '--title', title, '--username', username, '--password', password],
        env={**os.environ, **env},
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # 处理错误
        raise Exception(f"Failed to add password: {result.stderr}")

    return result.stdout
```

## 🚨 常见错误

### 错误 1: 缺少必需参数

```bash
pm --non-interactive add --title "GitHub"
# Error: Missing required parameter: --username is required in non-interactive mode
```

**解决**：提供所有必需参数
```bash
pm --non-interactive add \
  --title "GitHub" \
  --username "user@example.com" \
  --password "MyPassword123!"
```

### 错误 2: 缺少主密码

```bash
pm --non-interactive list
# Error: Master password not provided. Use --master-password argument or PM_MASTER_PASSWORD environment variable in non-interactive mode.
```

**解决**：设置主密码环境变量
```bash
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive list
```

### 错误 3: 删除缺少 --force

```bash
pm --non-interactive delete "GitHub"
# Error: Delete requires --force flag in non-interactive mode to skip confirmation.
```

**解决**：添加 `--force` 标志
```bash
pm --non-interactive delete "GitHub" --force
```

### 错误 4: 使用不支持的命令

```bash
pm --non-interactive edit "GitHub"
# Error: Edit command requires interactive mode. Use shell mode or interactive CLI for editing.
```

**解决**：在交互式模式下使用 `edit` 命令
```bash
pm edit "GitHub"
```

### 错误 5: 数据库已存在

```bash
pm --non-interactive init
# Error: Database already exists at /home/user/.pm.db. Use --force to overwrite or remove it manually.
```

**解决**：添加 `--force` 标志
```bash
pm --non-interactive init --force
```

## 🔄 迁移指南

### 从旧版本迁移

如果你之前没有使用 `--non-interactive`，现在可以直接使用：

```bash
# ✅ 新版本
export PM_MASTER_PASSWORD="your-password"
pm --non-interactive add --title "GitHub" --username "user" --password "pwd123"
```

### 从交互式迁移到非交互式

如果你有一个交互式脚本，想改为非交互式：

```bash
# ❌ 旧方式（交互式）
echo "Enter password:"
read password
pm add --title "GitHub" --username "user"

# ✅ 新方式（非交互式）
password="your-password"
pm --non-interactive add --title "GitHub" --username "user" --password "$password"
```

## 📚 集成示例

### Tauri (Rust)

```rust
use std::process::Command;

fn add_password(title: &str, username: &str, password: &str, master_password: &str) -> Result<String, String> {
    let output = Command::new("pm")
        .args(&[
            "add",
            "--title", title,
            "--username", username,
            "--password", password,
            "--non-interactive"
        ])
        .env("PM_MASTER_PASSWORD", master_password)
        .output()
        .map_err(|e| format!("Failed to execute pm: {}", e))?;

    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).to_string());
    }

    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}
```

### Electron (JavaScript)

```javascript
const { spawn } = require('child_process');

function addPassword(title, username, password, masterPassword) {
  return new Promise((resolve, reject) => {
    const env = {
      ...process.env,
      PM_MASTER_PASSWORD: masterPassword,
      PM_NON_INTERACTIVE: '1'
    };

    const args = [
      'add',
      '--title', title,
      '--username', username,
      '--password', password
    ];

    const process = spawn('pm', args, { env });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data;
    });

    process.stderr.on('data', (data) => {
      stderr += data;
    });

    process.on('close', (code) => {
      if (code === 0) {
        resolve(stdout);
      } else {
        reject(new Error(stderr || `Process exited with code ${code}`));
      }
    });
  });
}
```

### Python

```python
import subprocess
import os

def add_password(title: str, username: str, password: str, master_password: str) -> str:
    env = {
        **os.environ,
        'PM_MASTER_PASSWORD': master_password,
        'PM_NON_INTERACTIVE': '1'
    }

    result = subprocess.run(
        ['pm', 'add', '--title', title, '--username', username, '--password', password],
        env=env,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout

def delete_password(title: str, master_password: str) -> str:
    env = {
        **os.environ,
        'PM_MASTER_PASSWORD': master_password,
        'PM_NON_INTERACTIVE': '1'
    }

    result = subprocess.run(
        ['pm', 'delete', title, '--force'],
        env=env,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout
```

## 📚 参考文档

- [PM CLI 命令参考](./cli-guide.md)
- [GUI 集成指南](./gui-integration.md)
- [日志系统说明](./logging-guide.md)

---

**总结**：`--non-interactive` 标志和 `PM_NON_INTERACTIVE` 环境变量让 PM CLI 完全自动化，非常适合 GUI 应用、自动化脚本和 CI/CD 管道。在非交互模式下，所有必需参数都必须通过命令行提供，不会出现任何交互式提示。
