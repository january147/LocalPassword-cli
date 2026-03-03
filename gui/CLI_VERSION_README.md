# 密码管理器 GUI - CLI 版本文档

## 🎯 架构说明

本版本直接调用 Rust CLI 命令实现所有功能，不在 Python 中重复实现加密和数据库逻辑。

```
GUI (Python/Tkinter)
    ↓
subprocess 调用 CLI 命令
    ↓
Rust CLI (pm)
    ↓
加密数据库
```

## ✅ 功能支持

### 基础功能（通过 CLI 实现）

1. **数据库管理**
   - ✅ 新建数据库（`pm init --force`）
   - ✅ 打开数据库（`pm unlock <password>`）
   - ✅ 关闭数据库（清空 GUI 缓存）

2. **密码管理**
   - ✅ 添加密码（`pm add <title> <username> <password>`）
   - ✅ 编辑密码（`pm update <id>`）
   - ✅ 删除密码（`pm delete <id>`）
   - ✅ 列出密码（`pm list`）

3. **密码生成**
   - ✅ 生成密码（`pm generate`）
   - ✅ 自定义长度和字符类型
   - ✅ 自动复制到剪贴板

4. **数据管理**
   - ✅ 导出数据（`pm export <path>`）
   - ✅ 导入数据（`pm import <path>`）

5. **工具功能**
   - ✅ 数据库备份
   - ✅ 数据库恢复
   - ✅ 数据库清理

### GUI 功能

1. **界面组件**
   - ✅ 主界面（侧边栏 + 内容区）
   - ✅ 搜索和分类
   - ✅ 密码列表（表格显示）
   - ✅ 密码详情对话框
   - ✅ 密码生成器对话框
   - ✅ 右键菜单
   - ✅ 状态栏

2. **交互功能**
   - ✅ 实时搜索
   - ✅ 分类过滤
   - ✅ 双击快速编辑
   - ✅ 右键菜单
   - ✅ 加载动画
   - ✅ 状态提示

## 🚀 使用方法

### 前置条件

1. **编译 CLI**
   ```bash
   cd password-manager
   cargo build --release
   ```

2. **启动 GUI**
   
   **Linux/Mac**:
   ```bash
   # 给启动脚本添加执行权限
   chmod +x run_gui_cli.sh

   # 运行
   ./run_gui_cli.sh
   ```

   **Windows**:
   - 双击运行 `run_gui_cli.bat` 文件

### 首次使用

1. 启动 GUI
2. 点击"文件" → "新建数据库"
3. 输入主密码
4. 开始添加密码

### 日常使用

1. 启动 GUI
2. 输入主密码解锁数据库
3. 使用 GUI 功能管理密码

## 📋 CLI 命令参考

### 数据库操作

```bash
# 初始化数据库
pm init --force

# 解锁数据库
pm unlock <password>

# 清理数据库
pm cleanup
```

### 密码操作

```bash
# 列出所有密码
pm list

# 添加密码
pm add <title> <username> <password> [options]

# 更新密码
pm update <id> <title> <username> <password> [options]

# 删除密码
pm delete <id>
```

### 密码生成

```bash
# 生成密码（默认 16 位）
pm generate

# 指定长度
pm generate --length 20

# 字符选项
pm generate --uppercase --lowercase --numbers --symbols
```

### 数据管理

```bash
# 导出数据
pm export <output_path>

# 导入数据
pm import <input_path>
```

## 🎨 界面说明

### 主界面

```
┌────────┬─────────────────────────────────┐
│        │  搜索: [_______________]  [×] │
│  搜索  │                                │
│  ┌──┐  │  📂 分类                       │
│  │🔍│  │  ○ 所有                         │
│  └──┘  │  ○ 社交                         │
│        │  ○ 购物                         │
│  分类  │  ○ 工作                         │
│        │  ○ 其他                         │
│  所有   │                                │
│  社交   │  [添加密码]                   │
│  购物   │                                │
│  工作   │  密码列表 (5)                 │
│  其他   │  ┌──────────────────────────┐ │
│  ┌──┐  │  │ 🔐 Google               │ │
│  │➕│  │  │ user@gmail.com         │ │
│  └──┘  │  │ 🌟 Facebook            │ │
│        │  │ user@fb.com            │ │
│        │  └──────────────────────────┘ │
│        │                                │
└────────┴─────────────────────────────────┘
```

### 密码生成器

```
┌────────────────────────────────┐
│      🎲 密码生成器              [×]   │
├────────────────────────────────┤
│                                        │
│    生成的密码                          │
│    ┌─────────────────────────────┐    │
│    │ Xk9#mP2$vL8@nQ5!         │    │
│    └─────────────────────────────┘    │
│                                        │
│    [复制]  [重新生成]                 │
│                                        │
└────────────────────────────────┘
```

## 🔧 开发说明

### 如何扩展

如果 CLI 添加了新功能，只需：

1. 在 GUI 中添加对应的菜单项
2. 在 `run_pm_command` 中添加命令调用
3. 解析 CLI 输出并更新 GUI

### CLI 输出格式

CLI 应该输出 JSON 格式，方便 GUI 解析：

```json
{
  "id": "password_id",
  "title": "Google",
  "username": "user@gmail.com",
  "password": "password123",
  "website": "https://accounts.google.com",
  "category": "social",
  "created_at": "2024-03-03T12:00:00Z",
  "updated_at": "2024-03-03T12:00:00Z"
}
```

### 错误处理

CLI 应该在 stderr 中输出错误信息：

```bash
pm add "Test"
# stderr: Error: Database not initialized
```

GUI 会捕获 stderr 并显示错误提示。

---

**使用 CLI 快速完成，所有功能都已实现！** 🚀
