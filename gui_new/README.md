# Modern Password Manager GUI

一个现代化、美观且易用的密码管理器图形界面。

## ✨ 特性

### 界面设计
- 🎨 **现代化外观** - 采用 CustomTkinter 实现圆角、阴影、渐变配色
- 🌓 **深色/浅色主题** - 支持主题切换（默认深色）
- 📱 **响应式布局** - 自适应不同屏幕尺寸
- 🖼️ **图标化设计** - 直观的图标和视觉层次

### 核心功能
- 🔐 **安全登录** - 主密码加密保护
- 📋 **密码列表** - 卡片式展示，清晰易读
- 🔍 **实时搜索** - 即时过滤密码列表
- ➕ **快速添加** - 一键添加新密码
- ✏️ **编辑管理** - 轻松修改密码信息
- 🗑️ **安全删除** - 二次确认删除保护
- 📋 **一键复制** - 快速复制密码到剪贴板
- 🔢 **密码生成器** - 可自定义强度的密码生成
- 💾 **导出/导入** - JSON 格式数据备份

### 技术特性
- 🚀 **非交互式集成** - 基于 CLI 的非交互式模式
- 🧵 **多线程处理** - 异步操作，界面流畅
- ⚡ **即时反馈** - 加载状态和操作提示
- 🔒 **密码隐藏** - 默认隐藏，可显示

## 📦 安装

### 前置要求

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **Rust 编译的 pm CLI**
   ```bash
   cargo build --release
   # 确保 pm 在 PATH 中，或从项目目录运行
   ```

### 安装依赖

#### Linux/Mac
```bash
# 从项目根目录
cd password-manager

# 安装 Python 依赖
pip3 install -r gui_new/requirements.txt

# 或使用虚拟环境（推荐）
python3 -m venv gui_new/venv
source gui_new/venv/bin/activate
pip install -r gui_new/requirements.txt
```

#### Windows
```bash
# 从项目根目录
cd password-manager

# 安装 Python 依赖
pip install -r gui_new\requirements.txt

# 或使用虚拟环境（推荐）
python -m venv gui_new\venv
gui_new\venv\Scripts\activate
pip install -r gui_new\requirements.txt
```

## 🚀 运行

### 使用启动脚本（推荐）

#### Linux/Mac
```bash
chmod +x run_gui.sh
./run_gui.sh
```

#### Windows
```bash
run_gui.bat
```

### 直接运行
```bash
# 确保激活虚拟环境（如果使用）
source gui_new/venv/bin/activate  # Linux/Mac
# 或
gui_new\venv\Scripts\activate  # Windows

# 运行 GUI
python3 gui_new/password_manager.py
```

## 🎯 使用指南

### 登录
1. 输入主密码
2. 点击 "Unlock" 或按 Enter 键
3. 成功解锁后进入主界面

### 主界面布局

#### 左侧边栏
- 📋 Passwords - 密码列表
- ➕ Add New - 添加新密码
- 🔍 Search - 搜索密码
- ⚙️ Generator - 密码生成器
- 📤 Export - 导出密码
- 📥 Import - 导入密码
- 🔒 Lock - 锁定并返回登录页

#### 主内容区
- 搜索框
- 密码卡片列表
- 每个密码卡片包含：
  - 标题（加粗）
  - 用户名
  - URL（如果有）
  - 操作按钮：复制、编辑、删除

### 添加密码

1. 点击左侧边栏的 "➕ Add New"
2. 填写表单：
   - **Title** (必填) - 密码条目标题
   - **Username** (必填) - 用户名/邮箱
   - **Password** (必填) - 密码
   - **URL** (可选) - 网站 URL
   - **Category** (可选) - 分类标签
   - **Notes** (可选) - 备注信息
3. 点击 "🔢 Generate" 可以使用密码生成器
4. 点击 "Add Password" 保存

### 编辑密码

1. 在密码列表中找到要编辑的条目
2. 点击 "✏️ Edit" 按钮
3. 修改信息
4. 点击 "Save Password" 保存

### 删除密码

1. 在密码列表中找到要删除的条目
2. 点击 "🗑️ Delete" 按钮
3. 确认删除操作

### 搜索密码

1. 在顶部搜索框输入关键词
2. 列表会实时过滤显示匹配结果
3. 支持搜索：标题、用户名、URL

### 密码生成器

1. 点击左侧边栏的 "⚙️ Generator"
2. 调整滑块设置密码长度（8-64）
3. 点击 "🔄 Generate" 生成新密码
4. 点击 "📋 Copy" 复制到剪贴板
5. 点击 "✅ Use This" 使用生成的密码（返回添加/编辑表单）

### 导出密码

1. 点击左侧边栏的 "📤 Export"
2. 选择保存位置
3. 密码以 JSON 格式导出

### 导入密码

1. 点击左侧边栏的 "📥 Import"
2. 选择 JSON 文件
3. 确认导入
4. 密码会被添加到当前数据库

## 🔧 配置

### 主题切换

在代码中修改：
```python
# 在 password_manager.py 的 __init__ 方法中
ctk.set_appearance_mode("dark")  # dark/light/system
ctk.set_default_color_theme("blue")  # blue/green/dark-blue
```

### CLI 路径

如果 `pm` 不在 PATH 中，修改 `run_pm_command` 方法：
```python
result = subprocess.run(
    ['/path/to/pm', '--non-interactive'] + args,  # 修改 pm 的完整路径
    # ...
)
```

## 🎨 界面预览

### 登录页
- 简洁的登录界面
- 主密码输入框
- 显示/隐藏密码切换
- 品牌标语

### 主界面
- 左侧边栏导航
- 右侧内容区
- 顶部搜索框
- 密码卡片列表

### 密码卡片
- 标题（加粗）
- 用户名、URL
- 操作按钮（复制、编辑、删除）

### 密码生成器
- 长度滑块（8-64）
- 生成的密码显示
- 生成、复制、使用按钮

## 🐛 故障排除

### 问题：找不到 pm 命令

**解决方案：**
```bash
# 方法 1：添加到 PATH
export PATH="$PATH:/path/to/password-manager/target/release"

# 方法 2：使用完整路径
# 修改代码中的 subprocess.run，使用完整路径
```

### 问题：依赖安装失败

**解决方案：**
```bash
# 更新 pip
pip install --upgrade pip

# 使用国内镜像（如果在中国）
pip install -r gui_new/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题：GUI 无法启动

**检查清单：**
1. Python 版本是否 ≥ 3.8
2. pm CLI 是否已编译
3. 依赖是否已安装
4. 是否从项目根目录运行

### 问题：复制到剪贴板失败

**解决方案：**
```bash
# 安装 pyperclip
pip install pyperclip

# Linux 可能需要额外依赖
sudo apt-get install xclip  # X11
sudo apt-get install xsel    # X11
```

## 🔐 安全注意事项

1. **主密码安全**
   - 使用强主密码（至少 16 位）
   - 不要与他人共享
   - 定期更换（但需要重新加密数据库）

2. **数据备份**
   - 定期导出密码备份
   - 将备份文件存储在安全位置
   - 避免明文存储导出的 JSON

3. **剪贴板安全**
   - 复制后及时清除剪贴板
   - 避免长时间留在剪贴板
   - 使用密码管理器自动填充功能（如果支持）

4. **系统安全**
   - 锁定屏幕时关闭 GUI
   - 使用系统级加密
   - 保持系统和软件更新

## 📝 开发

### 项目结构

```
gui_new/
├── password_manager.py      # 主程序
├── requirements.txt        # Python 依赖
├── README.md             # 本文档
└── assets/              # 资源文件（未来添加）
```

### 扩展开发

可以添加的功能：
- [ ] 主题切换按钮
- [ ] 密码强度可视化
- [ ] 二维码扫描
- [ ] 云同步
- [ ] 浏览器集成
- [ ] 自动填充
- [ ] 两步验证
- [ ] 密码过期提醒

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](../LICENSE) 文件

## 📞 联系方式

- **项目主页**: https://github.com/january147/LocalPassword-cli
- **问题反馈**: https://github.com/january147/LocalPassword-cli/issues

---

**享受安全的密码管理体验！** 🔐
