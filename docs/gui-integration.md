# GUI 集成指南

本文档指导如何将 Password Manager CLI 集成到前端 GUI 应用中。

## 概述

Password Manager CLI (`pm`) 设计为支持完全非交互式操作，便于与各种前端 GUI 工具集成。

## 核心集成要点

### 1. 认证机制

CLI 工具提供三种认证方式，GUI 应用应优先使用以下方式：

#### 方式一：环境变量（推荐）

```python
import os
import subprocess

os.environ['PM_MASTER_PASSWORD'] = user_provided_password
result = subprocess.run(['pm', 'list'], capture_output=True, text=True)
```

优点：
- 不在命令行参数中暴露密码
- 简单易用
- 跨平台兼容

#### 方式二：命令行参数

```python
subprocess.run([
    'pm',
    '--master-password', user_provided_password,
    'list'
], capture_output=True, text=True)
```

⚠️ **安全提示**：命令行参数可能在进程监控工具中可见，不适合高安全需求场景。

#### 方式三：交互式输入（仅用于初始设置）

仅适用于初始化数据库等需要交互式输入的场景。

### 2. 非交互式模式

使用 `--non-interactive` 标志确保 CLI 不会尝试等待用户输入：

```python
subprocess.run([
    'pm',
    '--non-interactive',
    '--master-password', password,
    'list'
], capture_output=True, text=True)
```

## Python GUI 集成

### Tkinter 集成示例

```python
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os
import re

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.master_password = None

        self.setup_ui()

    def setup_ui(self):
        # 主密码输入
        tk.Label(self.root, text="Master Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", width=30)
        self.password_entry.pack(pady=5)

        # 连接按钮
        connect_btn = tk.Button(
            self.root,
            text="Connect",
            command=self.connect
        )
        connect_btn.pack(pady=10)

        # 搜索框
        tk.Label(self.root, text="Search:").pack(pady=5)
        self.search_entry = tk.Entry(self.root, width=30)
        self.search_entry.pack(pady=5)

        search_btn = tk.Button(
            self.root,
            text="Search",
            command=self.search_passwords
        )
        search_btn.pack(pady=10)

        # 结果列表
        self.result_list = tk.Listbox(self.root, width=50, height=20)
        self.result_list.pack(pady=10)
        self.result_list.bind('<Double-1>', self.on_select)

        # 详情显示
        self.detail_text = tk.Text(self.root, width=60, height=15)
        self.detail_text.pack(pady=10)

    def connect(self):
        """连接到密码数据库"""
        self.master_password = self.password_entry.get()
        if not self.master_password:
            messagebox.showerror("Error", "Please enter master password")
            return

        # 测试连接
        result = self.run_pm_command(['list'])
        if result.returncode != 0:
            messagebox.showerror("Error", "Failed to connect. Check master password.")
            self.master_password = None
        else:
            messagebox.showinfo("Success", "Connected successfully!")

    def run_pm_command(self, args):
        """执行 CLI 命令"""
        env = os.environ.copy()
        env['PM_MASTER_PASSWORD'] = self.master_password

        result = subprocess.run(
            ['pm', '--non-interactive'] + args,
            capture_output=True,
            text=True,
            env=env
        )
        return result

    def search_passwords(self):
        """搜索密码"""
        if not self.master_password:
            messagebox.showerror("Error", "Please connect first")
            return

        query = self.search_entry.get()
        if not query:
            result = self.run_pm_command(['list'])
        else:
            result = self.run_pm_command(['list', '--search', query])

        if result.returncode != 0:
            messagebox.showerror("Error", f"Command failed: {result.stderr}")
            return

        # 解析结果
        self.result_list.delete(0, tk.END)
        entries = self.parse_list_output(result.stdout)

        for entry in entries:
            self.result_list.insert(tk.END, f"{entry['title']} ({entry['username']})")
            self.result_list.itemconfig(tk.END, {'data': entry})

    def parse_list_output(self, output):
        """解析 CLI 输出"""
        entries = []
        current_entry = {}

        for line in output.split('\n'):
            if line.startswith('📌'):
                if current_entry:
                    entries.append(current_entry)
                # 提取标题
                title_match = re.search(r'📌\s+(.+)', line)
                current_entry = {'title': title_match.group(1) if title_match else ''}
            elif 'Username:' in line:
                username = line.split(':', 1)[1].strip()
                current_entry['username'] = username
            elif 'Password:' in line:
                password = line.split(':', 1)[1].strip()
                current_entry['password'] = password
            elif 'URL:' in line:
                url = line.split(':', 1)[1].strip()
                current_entry['url'] = url
            elif 'Category:' in line:
                category = line.split(':', 1)[1].strip()
                current_entry['category'] = category
            elif 'Notes:' in line:
                notes = line.split(':', 1)[1].strip()
                current_entry['notes'] = notes

        if current_entry:
            entries.append(current_entry)

        return entries

    def on_select(self, event):
        """显示选中密码的详情"""
        selection = self.result_list.curselection()
        if not selection:
            return

        entry = self.result_list.itemconfig(selection[0])['data']
        if isinstance(entry, dict):
            detail = f"Title: {entry.get('title', '')}\n"
            detail += f"Username: {entry.get('username', '')}\n"
            detail += f"Password: {entry.get('password', '******')}\n"
            if 'url' in entry:
                detail += f"URL: {entry['url']}\n"
            if 'category' in entry:
                detail += f"Category: {entry['category']}\n"
            if 'notes' in entry:
                detail += f"Notes: {entry['notes']}\n"

            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, detail)

if __name__ == '__main__':
    root = tk.Tk()
    app = PasswordManagerGUI(root)
    root.mainloop()
```

### PyQT5 集成示例

```python
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QListWidget,
                             QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt

class PasswordManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.master_password = None
        self.entries = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Password Manager')
        self.setGeometry(100, 100, 800, 600)

        widget = QWidget()
        layout = QVBoxLayout()

        # 主密码
        layout.addWidget(QLabel('Master Password:'))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        connect_btn = QPushButton('Connect')
        connect_btn.clicked.connect(self.connect)
        layout.addWidget(connect_btn)

        # 搜索
        layout.addWidget(QLabel('Search:'))
        self.search_input = QLineEdit()
        layout.addWidget(self.search_input)

        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.search)
        layout.addWidget(search_btn)

        # 结果列表
        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.show_details)
        layout.addWidget(self.result_list)

        # 详情
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        layout.addWidget(self.detail_text)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def run_pm_command(self, args):
        """执行 CLI 命令"""
        if not self.master_password:
            return None

        env = os.environ.copy()
        env['PM_MASTER_PASSWORD'] = self.master_password

        result = subprocess.run(
            ['pm', '--non-interactive'] + args,
            capture_output=True,
            text=True,
            env=env
        )
        return result

    def connect(self):
        """连接数据库"""
        password = self.password_input.text()
        if not password:
            QMessageBox.critical(self, 'Error', 'Please enter master password')
            return

        self.master_password = password
        result = self.run_pm_command(['list'])

        if result and result.returncode == 0:
            QMessageBox.information(self, 'Success', 'Connected successfully!')
            self.search()
        else:
            QMessageBox.critical(self, 'Error', 'Failed to connect')
            self.master_password = None

    def search(self):
        """搜索密码"""
        query = self.search_input.text()
        if not query:
            result = self.run_pm_command(['list'])
        else:
            result = self.run_pm_command(['list', '--search', query])

        if not result or result.returncode != 0:
            QMessageBox.critical(self, 'Error', 'Search failed')
            return

        self.entries = self.parse_output(result.stdout)
        self.result_list.clear()

        for entry in self.entries:
            self.result_list.addItem(f"{entry['title']} ({entry['username']})")

    def parse_output(self, output):
        """解析输出"""
        entries = []
        # 解析逻辑（类似 Tkinter 版本）
        return entries

    def show_details(self, item):
        """显示详情"""
        index = self.result_list.row(item)
        entry = self.entries[index]

        detail = f"Title: {entry.get('title', '')}\n"
        detail += f"Username: {entry.get('username', '')}\n"
        detail += f"Password: {entry.get('password', '******')}\n"
        # 添加其他字段...

        self.detail_text.setText(detail)

if __name__ == '__main__':
    app = QApplication([])
    window = PasswordManagerApp()
    window.show()
    app.exec_()
```

## Electron/JavaScript 集成

```javascript
const { spawn } = require('child_process');
const path = require('path');

class PasswordManager {
  constructor() {
    this.masterPassword = null;
  }

  setMasterPassword(password) {
    this.masterPassword = password;
  }

  runCommand(args) {
    return new Promise((resolve, reject) => {
      if (!this.masterPassword) {
        reject(new Error('Master password not set'));
        return;
      }

      const env = {
        ...process.env,
        PM_MASTER_PASSWORD: this.masterPassword
      };

      const pm = spawn('pm', ['--non-interactive', ...args], {
        env,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let stdout = '';
      let stderr = '';

      pm.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pm.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pm.on('close', (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(stderr || `Command failed with code ${code}`));
        }
      });
    });
  }

  async listPasswords() {
    const output = await this.runCommand(['list']);
    return this.parseListOutput(output);
  }

  async searchPasswords(query) {
    const output = await this.runCommand(['list', '--search', query]);
    return this.parseListOutput(output);
  }

  async getPassword(title) {
    const output = await this.runCommand(['get', title, '--show-password']);
    return this.parseGetOutput(output);
  }

  async addPassword(entry) {
    const args = ['add'];
    if (entry.title) args.push('--title', entry.title);
    if (entry.username) args.push('--username', entry.username);
    if (entry.password) args.push('--password', entry.password);
    if (entry.url) args.push('--url', entry.url);
    if (entry.category) args.push('--category', entry.category);

    await this.runCommand(args);
    return true;
  }

  parseListOutput(output) {
    // 解析逻辑
    return [];
  }

  parseGetOutput(output) {
    // 解析逻辑
    return {};
  }
}

// 使用示例
const pm = new PasswordManager();
pm.setMasterPassword('your_password');

// 获取所有密码
pm.listPasswords().then(entries => {
  console.log(entries);
}).catch(err => {
  console.error(err);
});
```

## React/Next.js 集成

### 后端 API (Node.js)

```javascript
// api/passwords.js
const express = require('express');
const { execSync } = require('child_process');
const os = require('os');

const router = express.Router();

function runPmCommand(args, masterPassword) {
  const env = {
    ...process.env,
    PM_MASTER_PASSWORD: masterPassword
  };

  try {
    const output = execSync(
      `pm --non-interactive ${args.join(' ')}`,
      { env, encoding: 'utf8' }
    );
    return { success: true, data: output };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

// 获取所有密码
router.get('/list', (req, res) => {
  const masterPassword = req.headers['x-master-password'];

  if (!masterPassword) {
    return res.status(401).json({ error: 'Master password required' });
  }

  const result = runPmCommand(['list'], masterPassword);

  if (result.success) {
    const entries = parseListOutput(result.data);
    res.json(entries);
  } else {
    res.status(500).json({ error: result.error });
  }
});

// 获取特定密码
router.get('/:title', (req, res) => {
  const masterPassword = req.headers['x-master-password'];
  const title = req.params.title;

  const result = runPmCommand(['get', title, '--show-password'], masterPassword);

  if (result.success) {
    const entry = parseGetOutput(result.data);
    res.json(entry);
  } else {
    res.status(500).json({ error: result.error });
  }
});

module.exports = router;
```

### 前端组件

```javascript
// components/PasswordList.js
import { useState, useEffect } from 'react';

export default function PasswordList({ masterPassword }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPasswords();
  }, [masterPassword]);

  const fetchPasswords = async () => {
    if (!masterPassword) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/passwords/list', {
        headers: {
          'X-Master-Password': masterPassword
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch passwords');
      }

      const data = await response.json();
      setEntries(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Password Entries</h2>
      <ul>
        {entries.map((entry, index) => (
          <li key={index}>
            <strong>{entry.title}</strong> ({entry.username})
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 安全考虑

### 1. 主密码存储

**不要在代码中硬编码主密码！**

推荐的安全存储方式：

```python
# 使用 keyring 库（Python）
import keyring

# 存储
keyring.set_password("password_manager", "user", "master_password")

# 读取
master_password = keyring.get_password("password_manager", "user")
```

```javascript
// 使用 electron-store（Electron）
const Store = require('electron-store');
const store = new Store();

// 存储（加密）
store.set('master_password', encrypt(password));

// 读取
const password = decrypt(store.get('master_password'));
```

### 2. 环境变量安全

```bash
# 不安全：历史会记录
export PM_MASTER_PASSWORD="password"

# 更安全：使用密钥管理器
PM_MASTER_PASSWORD=$(keychain get pm_password)
```

### 3. 输入验证

始终验证用户输入：

```python
def validate_title(title):
    if not title or len(title) > 256:
        raise ValueError("Invalid title")
    return title

def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password too short")
    return password
```

### 4. 错误处理

不要在错误消息中暴露敏感信息：

```python
try:
    result = self.run_pm_command(['get', title])
except Exception as e:
    # 不安全：logging.error(f"Failed with password {password}")
    # 安全：logging.error("Failed to retrieve password")
    logging.error("Failed to retrieve password")
    raise
```

## 输出解析指南

### list 输出格式

```
Found 2 entries:

📌 GitHub
  Username: user@example.com
  Password: ******
  URL: https://github.com
  Category: work

📌 Netflix
  Username: user@example.com
  Password: ******
  URL: https://netflix.com
  Category: personal
```

### get 输出格式

```
📌 GitHub
  Username: user@example.com
  Password: MySecurePassword
  URL: https://github.com
  Category: work
```

### 通用解析逻辑

```python
import re

def parse_pm_output(output):
    """通用解析函数"""
    entries = []
    current_entry = {}

    patterns = {
        'title': r'📌\s+(.+)',
        'username': r'Username:\s+(.+)',
        'password': r'Password:\s+(.+)',
        'url': r'URL:\s+(.+)',
        'category': r'Category:\s+(.+)',
        'notes': r'Notes:\s+(.+)',
    }

    for line in output.split('\n'):
        for key, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                value = match.group(1).strip()
                if key == 'title' and current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                current_entry[key] = value

    if current_entry:
        entries.append(current_entry)

    return entries
```

## 测试

### 单元测试

```python
import unittest
from unittest.mock import patch, MagicMock
import subprocess

class TestPasswordManagerGUI(unittest.TestCase):
    @patch('subprocess.run')
    def test_connect_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='')

        gui = PasswordManagerGUI(None)
        gui.master_password = "test_password"
        result = gui.run_pm_command(['list'])

        self.assertEqual(result.returncode, 0)
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_connect_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr='Wrong password')

        gui = PasswordManagerGUI(None)
        gui.master_password = "wrong_password"
        result = gui.run_pm_command(['list'])

        self.assertEqual(result.returncode, 1)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
import os
import subprocess

def test_cli_integration():
    """测试 CLI 集成"""
    os.environ['PM_MASTER_PASSWORD'] = 'test_password'

    # 初始化测试数据库
    result = subprocess.run(
        ['pm', 'init', '--force', '--db', '/tmp/test.db'],
        capture_output=True,
        text=True,
        input='test_password\ntest_password\n'
    )
    assert result.returncode == 0

    # 添加测试条目
    result = subprocess.run(
        ['pm', '--non-interactive', '--db', '/tmp/test.db',
         'add', '--title', 'Test', '--username', 'user',
         '--password', 'pass123'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

    # 列出条目
    result = subprocess.run(
        ['pm', '--non-interactive', '--db', '/tmp/test.db', 'list'],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert 'Test' in result.stdout
```

## 故障排除

### 常见问题

1. **命令找不到 pm**
   - 确保 pm 在 PATH 中
   - 使用完整路径

2. **权限错误**
   - 检查数据库文件权限
   - 确保 GUI 应用有读取权限

3. **主密码错误**
   - 验证主密码传递方式
   - 检查环境变量设置

4. **输出解析失败**
   - 检查 CLI 版本兼容性
   - 更新解析逻辑

## 参考资源

- [CLI 使用指南](./cli-guide.md)
- [项目主页](https://github.com/yourusername/password-manager)
- [问题反馈](https://github.com/yourusername/password-manager/issues)
