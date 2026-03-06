# GUI 集成指南

本文档指导如何将 Password Manager CLI 集成到前端 GUI 应用中。

## 📋 概述

Password Manager CLI (`pm`) 从 v0.1.0 开始支持**完全非交互式操作**，非常适合与各种前端 GUI 工具集成。

**核心要点：**

1. ✅ 使用 `--non-interactive` 标志或 `PM_NON_INTERACTIVE=1` 环境变量
2. ✅ 所有必需参数必须通过命令行提供
3. ✅ 使用环境变量 `PM_MASTER_PASSWORD` 传递主密码（推荐）
4. ✅ 捕获所有输出（stdout/stderr）进行处理
5. ✅ 根据返回码判断操作是否成功

## 🚀 快速开始

### 最小集成示例

```python
import subprocess
import os

def add_password(title, username, password, master_password):
    """添加密码 - 最简示例"""
    env = {
        'PM_MASTER_PASSWORD': master_password,
        'PM_NON_INTERACTIVE': '1'
    }

    result = subprocess.run(
        ['pm', 'add', '--title', title, '--username', username, '--password', password],
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=True  # 非 0 返回码会抛出异常
    )

    return result.stdout
```

## 🔧 核心集成要点

### 1. 认证机制

CLI 工具提供三种认证方式，GUI 应用应优先使用以下方式：

#### 方式一：环境变量（推荐）✅

```python
import os
import subprocess

def run_pm_command(args, master_password):
    """执行 PM CLI 命令 - 环境变量方式"""
    env = os.environ.copy()
    env['PM_MASTER_PASSWORD'] = master_password
    env['PM_NON_INTERACTIVE'] = '1'  # 启用非交互模式

    result = subprocess.run(
        ['pm'] + args,
        env=env,
        capture_output=True,
        text=True
    )

    return result

# 使用示例
result = run_pm_command(['list'], 'my_password')
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"Error: {result.stderr}")
```

**优点：**
- ✅ 不在命令行参数中暴露密码
- ✅ 简单易用
- ✅ 跨平台兼容
- ✅ 不会出现在进程列表中

#### 方式二：命令行参数（不推荐）❌

```python
subprocess.run([
    'pm',
    '--non-interactive',
    '--master-password', master_password,  # ⚠️ 不安全
    'list'
], capture_output=True, text=True)
```

⚠️ **安全提示**：命令行参数可能在进程监控工具中可见，不适合高安全需求场景。

### 2. 非交互式模式

**方式一：命令行标志**

```python
result = subprocess.run(
    ['pm', '--non-interactive', 'list'],
    env={'PM_MASTER_PASSWORD': password},
    capture_output=True,
    text=True
)
```

**方式二：环境变量**

```python
result = subprocess.run(
    ['pm', 'list'],
    env={
        'PM_MASTER_PASSWORD': password,
        'PM_NON_INTERACTIVE': '1'
    },
    capture_output=True,
    text=True
)
```

**两种方式都有效，推荐使用环境变量，代码更简洁。**

### 3. 必需参数

在非交互模式下，每个命令都有明确的必需参数要求：

| 命令 | 必需参数 |
|------|---------|
| `add` | `--title`, `--username`, `--password` 或 `--generate` |
| `delete` | title/id, `--force` |
| 其他命令 | 通常无需额外参数（需主密码） |

## 📚 Python GUI 集成

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
        """执行 CLI 命令 - 使用非交互模式"""
        env = os.environ.copy()
        env['PM_MASTER_PASSWORD'] = self.master_password
        env['PM_NON_INTERACTIVE'] = '1'

        result = subprocess.run(
            ['pm'] + args,
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

### PyQt5 集成示例

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
        """执行 CLI 命令 - 使用非交互模式"""
        if not self.master_password:
            return None

        env = os.environ.copy()
        env['PM_MASTER_PASSWORD'] = self.master_password
        env['PM_NON_INTERACTIVE'] = '1'

        result = subprocess.run(
            ['pm'] + args,
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
        current_entry = {}

        for line in output.split('\n'):
            if line.startswith('📌'):
                if current_entry:
                    entries.append(current_entry)
                title = line.replace('📌', '').strip()
                current_entry = {'title': title}
            elif 'Username:' in line:
                current_entry['username'] = line.split(':', 1)[1].strip()
            elif 'Password:' in line:
                current_entry['password'] = line.split(':', 1)[1].strip()
            elif 'URL:' in line:
                current_entry['url'] = line.split(':', 1)[1].strip()
            elif 'Category:' in line:
                current_entry['category'] = line.split(':', 1)[1].strip()
            elif 'Notes:' in line:
                current_entry['notes'] = line.split(':', 1)[1].strip()

        if current_entry:
            entries.append(current_entry)

        return entries

    def show_details(self, item):
        """显示详情"""
        index = self.result_list.row(item)
        entry = self.entries[index]

        detail = f"Title: {entry.get('title', '')}\n"
        detail += f"Username: {entry.get('username', '')}\n"
        detail += f"Password: {entry.get('password', '******')}\n"

        if 'url' in entry:
            detail += f"URL: {entry['url']}\n"
        if 'category' in entry:
            detail += f"Category: {entry['category']}\n"
        if 'notes' in entry:
            detail += f"Notes: {entry['notes']}\n"

        self.detail_text.setText(detail)

if __name__ == '__main__':
    app = QApplication([])
    window = PasswordManagerApp()
    window.show()
    app.exec_()
```

## 💻 Electron/JavaScript 集成

### 完整封装类

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
        PM_MASTER_PASSWORD: this.masterPassword,
        PM_NON_INTERACTIVE: '1'
      };

      const pm = spawn('pm', args, {
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

    if (!entry.title) {
      throw new Error('Title is required in non-interactive mode');
    }
    if (!entry.username) {
      throw new Error('Username is required in non-interactive mode');
    }
    if (!entry.password && !entry.generate) {
      throw new Error('Password or generate length is required in non-interactive mode');
    }

    args.push('--title', entry.title);
    args.push('--username', entry.username);

    if (entry.password) {
      args.push('--password', entry.password);
    } else if (entry.generate) {
      args.push('--generate', String(entry.generate));
    }

    if (entry.url) args.push('--url', entry.url);
    if (entry.category) args.push('--category', entry.category);
    if (entry.notes) args.push('--notes', entry.notes);

    await this.runCommand(args);
    return true;
  }

  async deletePassword(title) {
    await this.runCommand(['delete', title, '--force']);
    return true;
  }

  parseListOutput(output) {
    const entries = [];
    const lines = output.split('\n');
    let currentEntry = {};

    for (const line of lines) {
      if (line.startsWith('📌')) {
        if (Object.keys(currentEntry).length > 0) {
          entries.push(currentEntry);
        }
        currentEntry = { title: line.replace('📌', '').trim() };
      } else if (line.includes('Username:')) {
        currentEntry.username = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('Password:')) {
        currentEntry.password = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('URL:')) {
        currentEntry.url = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('Category:')) {
        currentEntry.category = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('Notes:')) {
        currentEntry.notes = line.split(':').slice(1).join(':').trim();
      }
    }

    if (Object.keys(currentEntry).length > 0) {
      entries.push(currentEntry);
    }

    return entries;
  }

  parseGetOutput(output) {
    const lines = output.split('\n');
    const entry = {};

    for (const line of lines) {
      if (line.includes('Title:') || line.startsWith('📌')) {
        entry.title = line.replace('📌', '').replace('Title:', '').trim();
      } else if (line.includes('Username:')) {
        entry.username = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('Password:')) {
        entry.password = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('URL:')) {
        entry.url = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('Category:')) {
        entry.category = line.split(':').slice(1).join(':').trim();
      } else if (line.includes('Notes:')) {
        entry.notes = line.split(':').slice(1).join(':').trim();
      }
    }

    return entry;
  }
}

// 使用示例
const pm = new PasswordManager();
pm.setMasterPassword('your_password');

// 获取所有密码
pm.listPasswords().then(entries => {
  console.log('Entries:', entries);
}).catch(err => {
  console.error('Error:', err.message);
});

// 添加密码
pm.addPassword({
  title: 'GitHub',
  username: 'user@example.com',
  password: 'MyPassword123!',
  url: 'https://github.com',
  category: 'Development'
}).then(() => {
  console.log('Password added successfully');
}).catch(err => {
  console.error('Error adding password:', err.message);
});

// 删除密码
pm.deletePassword('GitHub').then(() => {
  console.log('Password deleted successfully');
}).catch(err => {
  console.error('Error deleting password:', err.message);
});
```

## 🌐 React/Next.js 集成

### 后端 API (Node.js/Express)

```javascript
// api/passwords.js
const express = require('express');
const { spawn } = require('child_process');
const router = express.Router();

function runPmCommand(args, masterPassword) {
  return new Promise((resolve, reject) => {
    const env = {
      ...process.env,
      PM_MASTER_PASSWORD: masterPassword,
      PM_NON_INTERACTIVE: '1'
    };

    const pm = spawn('pm', args, {
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

// 获取所有密码
router.get('/list', async (req, res) => {
  const masterPassword = req.headers['x-master-password'];

  if (!masterPassword) {
    return res.status(401).json({ error: 'Master password required' });
  }

  try {
    const output = await runPmCommand(['list'], masterPassword);
    const entries = parseListOutput(output);
    res.json(entries);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 获取特定密码
router.get('/:title', async (req, res) => {
  const masterPassword = req.headers['x-master-password'];
  const title = req.params.title;

  try {
    const output = await runPmCommand(['get', title, '--show-password'], masterPassword);
    const entry = parseGetOutput(output);
    res.json(entry);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 添加密码
router.post('/', async (req, res) => {
  const masterPassword = req.headers['x-master-password'];
  const { title, username, password, generate, url, category, notes } = req.body;

  if (!title || !username) {
    return res.status(400).json({ error: 'Title and username are required' });
  }

  if (!password && !generate) {
    return res.status(400).json({ error: 'Password or generate length is required' });
  }

  try {
    const args = ['add', '--title', title, '--username', username];

    if (password) {
      args.push('--password', password);
    } else {
      args.push('--generate', String(generate));
    }

    if (url) args.push('--url', url);
    if (category) args.push('--category', category);
    if (notes) args.push('--notes', notes);

    await runPmCommand(args, masterPassword);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 删除密码
router.delete('/:title', async (req, res) => {
  const masterPassword = req.headers['x-master-password'];
  const title = req.params.title;

  try {
    await runPmCommand(['delete', title, '--force'], masterPassword);
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

function parseListOutput(output) {
  // 解析逻辑（参考 JavaScript 版本）
  return [];
}

function parseGetOutput(output) {
  // 解析逻辑（参考 JavaScript 版本）
  return {};
}

module.exports = router;
```

### 前端 React 组件

```javascript
// components/PasswordManager.js
import { useState, useEffect } from 'react';

export default function PasswordManager({ masterPassword }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (masterPassword) {
      fetchPasswords();
    }
  }, [masterPassword, searchQuery]);

  const fetchPasswords = async () => {
    if (!masterPassword) return;

    setLoading(true);
    setError(null);

    try {
      let url = '/api/passwords/list';
      if (searchQuery) {
        url = `/api/passwords/list?search=${encodeURIComponent(searchQuery)}`;
      }

      const response = await fetch(url, {
        headers: {
          'X-Master-Password': masterPassword
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch passwords');
      }

      const data = await response.json();
      setEntries(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPassword = async (entry) => {
    try {
      const response = await fetch('/api/passwords', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Master-Password': masterPassword
        },
        body: JSON.stringify(entry)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to add password');
      }

      await fetchPasswords();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  const handleDeletePassword = async (title) => {
    try {
      const response = await fetch(`/api/passwords/${encodeURIComponent(title)}`, {
        method: 'DELETE',
        headers: {
          'X-Master-Password': masterPassword
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete password');
      }

      await fetchPasswords();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Password Manager</h2>

      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Search..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ padding: '8px', width: '300px' }}
        />
      </div>

      <ul style={{ listStyle: 'none', padding: 0 }}>
        {entries.map((entry, index) => (
          <li key={index} style={{
            border: '1px solid #ddd',
            padding: '10px',
            margin: '5px 0',
            borderRadius: '4px'
          }}>
            <strong>{entry.title}</strong> ({entry.username})
            <button
              onClick={() => handleDeletePassword(entry.title)}
              style={{ marginLeft: '10px' }}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 🔐 安全考虑

### 1. 主密码存储

**不要在代码中硬编码主密码！**

#### 推荐的安全存储方式

**Python - 使用 keyring:**

```python
import keyring

# 存储
keyring.set_password("password_manager", "user", "master_password")

# 读取
master_password = keyring.get_password("password_manager", "user")

# 删除
keyring.delete_password("password_manager", "user")
```

**JavaScript/Electron - 使用 electron-store 加密:**

```javascript
const Store = require('electron-store');
const crypto = require('crypto');

const store = new Store();

// 加密函数
function encrypt(text, key) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(key), iv);
  let encrypted = cipher.update(text);
  encrypted = Buffer.concat([encrypted, cipher.final()]);
  return iv.toString('hex') + ':' + encrypted.toString('hex');
}

// 解密函数
function decrypt(text, key) {
  const parts = text.split(':');
  const iv = Buffer.from(parts[0], 'hex');
  const encrypted = Buffer.from(parts[1], 'hex');
  const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(key), iv);
  let decrypted = decipher.update(encrypted);
  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return decrypted.toString();
}

// 存储
const encryptionKey = crypto.randomBytes(32).toString('hex');
store.set('master_password', encrypt(password, encryptionKey));
store.set('encryption_key', encryptionKey);

// 读取
const encryptionKey = store.get('encryption_key');
const password = decrypt(store.get('master_password'), encryptionKey);
```

### 2. 环境变量安全

```bash
# ❌ 不安全：历史会记录
export PM_MASTER_PASSWORD="password"

# ✅ 更安全：使用密钥管理器
PM_MASTER_PASSWORD=$(keychain get pm_password)

# ✅ 最安全：子 shell 中设置
(PM_MASTER_PASSWORD="$(get-password)" pm --non-interactive list)
```

### 3. 输入验证

始终验证用户输入：

```python
def validate_title(title):
    if not title:
        raise ValueError("Title is required")
    if len(title) > 256:
        raise ValueError("Title too long (max 256 characters)")
    # 移除危险字符
    return re.sub(r'[\n\r\t]', '', title)

def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password too short (min 8 characters)")
    if len(password) > 1024:
        raise ValueError("Password too long (max 1024 characters)")
    return password

# 使用
validated_title = validate_title(user_input_title)
validated_password = validate_password(user_input_password)

pm.add_password(validated_title, username, validated_password)
```

### 4. 错误处理

不要在错误消息中暴露敏感信息：

```python
# ❌ 不安全
try:
    result = self.run_pm_command(['get', title])
except Exception as e:
    logging.error(f"Failed with password {password}")  # 暴露密码！
    raise

# ✅ 安全
try:
    result = self.run_pm_command(['get', title])
except Exception as e:
    logging.error("Failed to retrieve password")  # 不暴露敏感信息
    raise
```

## 📝 输出解析指南

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

### 通用解析逻辑（Python）

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

## 🧪 测试

### 单元测试（Python）

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
        # 验证是否传递了正确的环境变量
        call_args = mock_run.call_args
        self.assertIn('PM_MASTER_PASSWORD', call_args.kwargs['env'])
        self.assertIn('PM_NON_INTERACTIVE', call_args.kwargs['env'])

    @patch('subprocess.run')
    def test_connect_failure(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr='Wrong password'
        )

        gui = PasswordManagerGUI(None)
        gui.master_password = "wrong_password"
        result = gui.run_pm_command(['list'])

        self.assertEqual(result.returncode, 1)

    @patch('subprocess.run')
    def test_non_interactive_mode(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='')

        gui = PasswordManagerGUI(None)
        gui.master_password = "test_password"
        gui.run_pm_command(['add', '--title', 'Test', '--username', 'user', '--password', 'pass'])

        # 验证环境变量包含 PM_NON_INTERACTIVE
        call_args = mock_run.call_args
        self.assertEqual(call_args.kwargs['env']['PM_NON_INTERACTIVE'], '1')

if __name__ == '__main__':
    unittest.main()
```

### 集成测试（Python）

```python
import os
import subprocess
import tempfile

def test_cli_integration():
    """测试 CLI 集成 - 非交互模式"""
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # 初始化测试数据库
        result = subprocess.run(
            ['pm', 'init', '--db', db_path, '--force'],
            capture_output=True,
            text=True,
            input='test_password\ntest_password\n'
        )
        assert result.returncode == 0, f"Init failed: {result.stderr}"

        # 测试非交互模式添加密码
        result = subprocess.run(
            ['pm', '--db', db_path, '--non-interactive', 'add',
             '--title', 'Test', '--username', 'user', '--password', 'pass123'],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                'PM_MASTER_PASSWORD': 'test_password'
            }
        )
        assert result.returncode == 0, f"Add failed: {result.stderr}"

        # 测试非交互模式列出密码
        result = subprocess.run(
            ['pm', '--db', db_path, '--non-interactive', 'list'],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                'PM_MASTER_PASSWORD': 'test_password'
            }
        )
        assert result.returncode == 0, f"List failed: {result.stderr}"
        assert 'Test' in result.stdout, "Test entry not found"

        # 测试非交互模式删除密码
        result = subprocess.run(
            ['pm', '--db', db_path, '--non-interactive', 'delete', 'Test', '--force'],
            capture_output=True,
            text=True,
            env={
                **os.environ,
                'PM_MASTER_PASSWORD': 'test_password'
            }
        )
        assert result.returncode == 0, f"Delete failed: {result.stderr}"

        print("All integration tests passed!")

    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == '__main__':
    test_cli_integration()
```

## 🔧 故障排除

### 常见问题

#### 1. 命令找不到 pm

**错误信息：**
```
Error: Command not found: pm
```

**解决方案：**
- 确保 pm 在 PATH 中
- 使用完整路径：`/usr/local/bin/pm`
- 在 GUI 应用配置中设置 pm 路径

```python
# 设置 pm 路径
PM_PATH = os.environ.get('PM_PATH', '/usr/local/bin/pm')

result = subprocess.run(
    [PM_PATH, 'list'],
    ...
)
```

#### 2. 权限错误

**错误信息：**
```
Error: Permission denied: /home/user/.pm.db
```

**解决方案：**
- 检查数据库文件权限
- 确保 GUI 应用有读取/写入权限
- 使用自定义数据库路径

```python
# 使用自定义数据库路径
result = subprocess.run(
    ['pm', '--db', '/path/to/custom.db', 'list'],
    ...
)
```

#### 3. 主密码错误

**错误信息：**
```
Error: Failed to open database. Check your master password.
```

**解决方案：**
- 验证主密码传递方式
- 检查环境变量设置
- 确保没有特殊字符导致问题

```python
# 添加调试日志
logging.debug(f"Master password length: {len(master_password)}")
logging.debug(f"PM_MASTER_PASSWORD in env: {'PM_MASTER_PASSWORD' in env}")
```

#### 4. 缺少必需参数

**错误信息：**
```
Error: Missing required parameter: --username is required in non-interactive mode
```

**解决方案：**
- 在非交互模式下，所有必需参数必须提供
- 检查命令行参数是否完整

```python
# ✅ 正确
result = subprocess.run([
    'pm', '--non-interactive', 'add',
    '--title', title,
    '--username', username,
    '--password', password
], ...)

# ❌ 错误 - 缺少 --username
result = subprocess.run([
    'pm', '--non-interactive', 'add',
    '--title', title,
    '--password', password
], ...)
```

#### 5. 输出解析失败

**错误信息：**
```
Error: Failed to parse output
```

**解决方案：**
- 检查 CLI 版本兼容性
- 更新解析逻辑
- 查看原始输出进行调试

```python
# 添加调试输出
def parse_output(output):
    logging.debug(f"Raw output: {repr(output)}")
    # 解析逻辑...
```

## 📚 参考资源

- [非交互式模式详细说明](./non-interactive-mode.md)
- [CLI 命令参考](./cli-guide.md)
- [日志系统说明](./logging-guide.md)
- [项目主页](https://github.com/yourusername/password-manager)
- [问题反馈](https://github.com/yourusername/password-manager/issues)

---

**总结**：使用 `--non-interactive` 标志或 `PM_NON_INTERACTIVE` 环境变量，PM CLI 可以完美集成到各种 GUI 应用中。关键点：
1. 使用环境变量传递主密码
2. 提供所有必需参数
3. 捕获并正确处理输出
4. 实现健壮的错误处理
5. 遵循安全最佳实践
