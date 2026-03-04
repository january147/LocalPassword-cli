# Logging Guide

Password Manager CLI 提供了完善的日志功能，默认关闭以优化性能。可以通过命令行参数或环境变量启用。

## 启用日志

### 方式一：命令行参数

```bash
# 启用日志（默认 info 级别）
pm --log list

# 指定日志级别
pm --log --log-level debug list

# 关闭日志（默认行为）
pm list
```

### 方式二：环境变量

```bash
# 启用日志
export PM_LOG=1
pm list

# 指定日志级别
export PM_LOG_LEVEL=debug
pm list

# 禁用日志（默认）
unset PM_LOG
```

## 日志级别

支持的日志级别（从低到高）：

| 级别 | 说明 | 用途 |
|------|------|------|
| `off` | 完全关闭 | 生产环境（默认） |
| `error` | 仅错误 | 调试错误 |
| `warn` | 警告和错误 | 生产环境监控 |
| `info` | 信息、警告、错误 | 一般调试（启用时默认） |
| `debug` | 调试信息 | 详细调试 |
| `trace` | 所有信息 | 完整追踪 |

### 示例

```bash
# 仅错误
pm --log --log-level error list

# 警告和错误
pm --log --log-level warn list

# 信息及以上（默认）
pm --log list

# 调试信息
pm --log --log-level debug list

# 完整追踪
pm --log --log-level trace list
```

## 日志内容

### info 级别示例

```bash
$ pm --log list
[2026-03-04 10:45:00] INFO [password_manager_cli]: Password Manager CLI starting...
[2026-03-04 10:45:00] INFO [password_manager_cli]: Using database at: /home/user/.pm.db
[2026-03-04 10:45:00] INFO [password_manager_cli]: Opening database...
[2026-03-04 10:45:01] INFO [password_manager_cli]: Database opened successfully
[2026-03-04 10:45:01] INFO [password_manager_cli]: Listing passwords (category: None, search: None)
[2026-03-04 10:45:01] INFO [password_manager_cli]: Found 5 entries before filtering
```

### debug 级别示例

```bash
$ pm --log --log-level debug list
[2026-03-04 10:45:00] DEBUG [password_manager_cli]: Parsed CLI arguments: Cli { db: None, master_password: None, non_interactive: false, log: true, log_level: "debug", command: List { category: None, search: None, show_passwords: false } }
[2026-03-04 10:45:00] INFO [password_manager_cli]: Password Manager CLI starting...
[2026-03-04 10:45:00] DEBUG [password_manager_cli]: Attempting to open database at: /home/user/.pm.db
[2026-03-04 10:45:00] DEBUG [password_manager_cli]: Prompting for master password interactively
[2026-03-04 10:45:00] INFO [password_manager_cli]: Using database at: /home/user/.pm.db
[2026-03-04 10:45:00] INFO [password_manager_cli]: Opening database...
[2026-03-04 10:45:01] INFO [password_manager_cli]: Database opened successfully
[2026-03-04 10:45:01] INFO [password_manager_cli]: Listing passwords (category: None, search: None)
[2026-03-04 10:45:01] DEBUG [password_manager_cli]: Found 5 entries before filtering
```

### error 级别示例

```bash
$ pm --log --log-level error get InvalidTitle
[2026-03-04 10:45:00] ERROR [password_manager_cli]: Failed to open database: Failed to decrypt database
Error: Failed to decrypt database
```

## 常用场景

### 调试密码添加问题

```bash
pm --log --log-level debug add --title "Test"
```

### 监控数据库操作

```bash
pm --log list
pm --log get "GitHub"
pm --log delete "OldAccount"
```

### 生产环境错误监控

```bash
export PM_LOG=1
export PM_LOG_LEVEL=warn
pm list
```

### GUI 集成调试

```bash
# 在集成 GUI 工具时启用日志
export PM_LOG=1
export PM_LOG_LEVEL=debug
your-gui-app
```

## 日志安全注意事项

### ⚠️ 重要安全提示

1. **不要在日志中记录敏感信息**
   - 日志不会记录明文密码
   - 日志不会记录主密码
   - 但请检查日志级别，避免记录过多上下文

2. **生产环境建议**
   - 默认关闭日志 (`off` 或 `warn`)
   - 定期清理日志文件
   - 不要将日志文件提交到版本控制

3. **日志文件位置**
   - 日志输出到标准错误 (stderr)
   - 可以重定向到文件：
     ```bash
     pm --log --log-level info list 2>&1 | tee pm.log
     ```

4. **日志级别选择**
   - 生产环境：`warn` 或 `error`
   - 开发环境：`debug` 或 `trace`
   - 调试问题：`debug` 或 `trace`

## 性能影响

- **日志关闭（默认）**：零性能开销
- **info 级别**：轻微性能影响 (~1-2%)
- **debug 级别**：中等性能影响 (~5-10%)
- **trace 级别**：较高性能影响 (~10-20%)

建议在性能敏感的场景关闭日志或使用 `warn` 级别。

## 故障排除

### 问题：日志没有输出

**可能原因：**
- 没有使用 `--log` 参数
- 没有设置 `PM_LOG` 环境变量
- 日志级别设置为 `off`

**解决方法：**
```bash
pm --log --log-level info list
```

### 问题：日志信息太多

**可能原因：**
- 使用了 `debug` 或 `trace` 级别

**解决方法：**
```bash
# 降低日志级别
pm --log --log-level warn list
```

### 问题：看不到错误信息

**可能原因：**
- 日志级别设置为 `off`

**解决方法：**
```bash
pm --log --log-level error list
```

## 完整示例

### 场景 1：添加密码并查看详细日志

```bash
pm --log --log-level debug add --title "GitHub" --username "user@example.com" --generate
```

输出示例：
```
[2026-03-04 10:45:00] DEBUG [password_manager_cli]: Parsed CLI arguments: ...
[2026-03-04 10:45:00] INFO [password_manager_cli]: Password Manager CLI starting...
[2026-03-04 10:45:00] INFO [password_manager_cli]: Using database at: /home/user/.pm.db
[2026-03-04 10:45:00] DEBUG [password_manager_cli]: Using master password from PM_MASTER_PASSWORD env var
[2026-03-04 10:45:00] INFO [password_manager_cli]: Opening database...
[2026-03-04 10:45:01] INFO [password_manager_cli]: Database opened successfully
[2026-03-04 10:45:01] INFO [password_manager_cli]: Adding new password entry...
[2026-03-04 10:45:01] INFO [password_manager_cli]: Adding password entry: title='GitHub', username='user@example.com'
[2026-03-04 10:45:01] INFO [password_manager_cli]: Password entry added successfully

Generated password: AbCdEf123!@#XyZ

✓ Password entry added successfully!
```

### 场景 2：删除密码并监控操作

```bash
export PM_LOG=1
export PM_LOG_LEVEL=info
pm delete "OldAccount"
```

### 场景 3：GUI 集成调试

```python
import subprocess
import os

# 启用日志
env = os.environ.copy()
env['PM_LOG'] = '1'
env['PM_LOG_LEVEL'] = 'debug'
env['PM_MASTER_PASSWORD'] = 'your_password'

# 运行命令并捕获日志
result = subprocess.run(
    ['pm', '--non-interactive', 'list'],
    capture_output=True,
    text=True,
    env=env
)

# 输出日志和结果
print("STDOUT:", result.stdout)
print("STDERR (logs):", result.stderr)
```

## 参考资源

- [CLI 使用指南](./cli-guide.md)
- [GUI 集成指南](./gui-integration.md)
- [项目主页](https://github.com/yourusername/password-manager)
