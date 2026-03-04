# PM CLI 非交互式模式说明

## ✅ 重要更新

从 v0.1.0 开始，**`--non-interactive` 选项已被移除**。

### 原因

`--non-interactive` 选项实际上没有发挥作用，因为：

1. **命令已经支持非交互式使用** - 如果所有参数都通过命令行提供，不会出现交互式提示
2. **只在缺少必需参数时才提示** - 如果某些参数没有提供，才会使用 `dialoguer` 提示用户输入
3. **简化了接口** - 移除不必要的参数，使 API 更简洁

### 新的工作方式

现在 PM CLI 的工作方式更简单：

- ✅ **如果所有参数通过命令行提供** → 完全非交互式，直接执行
- ✅ **如果某些参数未提供** → 交互式提示用户输入缺失的参数
- ✅ **如果没有提供主密码** → 交互式提示输入主密码（或使用 `PM_MASTER_PASSWORD` 环境变量）

## 🚀 非交互式使用示例

### 完整参数（完全非交互式）

```bash
# 添加密码 - 所有参数都提供了
pm add \
  --title "GitHub" \
  --username "user@example.com" \
  --password "MyPassword123!" \
  --url "https://github.com" \
  --category "Development" \
  --notes "Main GitHub account"

# 使用主密码环境变量
export PM_MASTER_PASSWORD="your-master-password"
pm add --title "GitHub" --username "user@example.com" --password "MyPassword123!"
```

### 自动生成密码（非交互式）

```bash
# 指定长度自动生成密码
pm add \
  --title "GitHub" \
  --username "user@example.com" \
  --generate 20
```

### 列出密码（非交互式）

```bash
# 列出所有密码
export PM_MASTER_PASSWORD="your-master-password"
pm list

# 按类别过滤
pm list --category "Development"

# 搜索
pm list --search "GitHub"
```

### 删除密码（非交互式）

```bash
# 使用 --force 跳过确认
export PM_MASTER_PASSWORD="your-master-password"
pm delete "GitHub" --force
```

### 导出/导入（非交互式）

```bash
# 导出
export PM_MASTER_PASSWORD="your-master-password"
pm export /path/to/backup.json

# 导入
export PM_MASTER_PASSWORD="your-master-password"
pm import /path/to/backup.json
```

## 🎯 GUI 集成指南

### 前端集成

在 GUI 应用中调用 PM CLI 时，只需提供所有必需参数：

```javascript
// 前端示例
const { spawn } = require('child_process');

// 设置环境变量
const env = {
  ...process.env,
  PM_MASTER_PASSWORD: masterPassword
};

// 添加密码
const args = [
  'add',
  '--title', title,
  '--username', username,
  '--password', password,
  '--url', url,
  '--category', category,
  '--notes', notes
];

spawn('pm', args, { env });
```

### Tauri 集成

在 Tauri 应用中：

```rust
// Rust backend
use std::process::Command;

let result = Command::new("pm")
    .args(&[
        "add",
        "--title", &title,
        "--username", &username,
        "--password", &password,
    ])
    .env("PM_MASTER_PASSWORD", &master_password)
    .output()?;
```

## 📝 主密码传递

### 方式一：环境变量（推荐）

```bash
export PM_MASTER_PASSWORD="your-master-password"
pm add --title "GitHub" --username "user@example.com" --password "MyPassword123!"
```

### 方式二：命令行参数（不推荐）

```bash
pm add \
  --master-password "your-master-password" \
  --title "GitHub" \
  --username "user@example.com" \
  --password "MyPassword123!"
```

**⚠️ 注意：** 命令行方式不推荐，因为密码会出现在进程列表和命令历史中。

### 方式三：交互式提示（仅 CLI 使用）

如果没有提供主密码，PM CLI 会交互式提示用户输入：

```bash
pm list
# 会提示: Enter master password: [隐藏输入]
```

## 🔧 交互式使用示例

### 添加密码（交互式）

```bash
# 只提供部分参数，其他参数会提示输入
pm add --title "GitHub"
# 提示: Username: [输入]
# 提示: Generate a strong password? [Y/n]: [选择]
# 提示: Password: [如果选择不自动生成]
# 提示: URL (optional): [输入或跳过]
# 提示: Category (optional): [输入或跳过]
```

### 编辑密码（交互式）

```bash
# 只提供标题，其他字段会提示修改
pm edit "GitHub"
# 显示当前信息
# 提示: Title [GitHub]: [按Enter保持不变或输入新值]
# 提示: Username [user@example.com]: [按Enter保持不变或输入新值]
# 提示: Password (press Enter to keep current): [按Enter保持或输入新密码]
```

## 💡 最佳实践

### 1. GUI 集成

✅ **使用环境变量传递主密码**
✅ **提供所有必需参数**
✅ **不依赖交互式提示**

### 2. 脚本自动化

✅ **在脚本开头设置 `PM_MASTER_PASSWORD`**
✅ **使用完整参数避免提示**
✅ **使用 `--force` 跳过确认**

```bash
#!/bin/bash
export PM_MASTER_PASSWORD="$(get-password-from-keyring)"

# 添加密码
pm add --title "GitHub" --username "user" --password "pwd123"

# 删除密码（跳过确认）
pm delete "GitHub" --force
```

### 3. 安全注意事项

❌ **不要在命令行中传递密码**（会出现在进程列表和 shell 历史）
❌ **不要在日志中记录密码**
❌ **不要在不信任的环境中设置 `PM_MASTER_PASSWORD`**

✅ **使用环境变量传递敏感信息**
✅ **使用密钥管理工具存储主密码**
✅ **在子 shell 中设置环境变量**

```bash
# ✅ 好的做法
(PM_MASTER_PASSWORD="$(get-password)" pm list)

# ❌ 不好的做法
echo "PM_MASTER_PASSWORD=secret123" >> ~/.bashrc
```

## 🔄 迁移指南

### 从旧版本迁移

如果你之前使用 `--non-interactive`，现在只需移除它：

```bash
# ❌ 旧版本（已废弃）
pm --non-interactive add --title "GitHub" --username "user" --password "pwd123"

# ✅ 新版本（推荐）
pm add --title "GitHub" --username "user" --password "pwd123"
```

### 不需要的改变

只要你的代码/脚本已经提供所有必需参数，就不需要做任何改变！

```bash
# 这些命令一直都能工作，现在更简洁了
export PM_MASTER_PASSWORD="your-password"
pm add --title "GitHub" --username "user" --password "pwd123"
pm list
pm delete "GitHub" --force
```

## 📚 参考文档

- [PM CLI 命令参考](./cli-guide.md)
- [GUI 集成指南](./gui-integration.md)
- [日志系统说明](./logging-guide.md)

---

**总结：** 移除 `--non-interactive` 后，PM CLI 的使用更简单自然。如果提供所有参数，它就是非交互式的；如果缺少参数，它会智能地提示用户输入。这样既支持自动化脚本，也保持了良好的用户体验。
