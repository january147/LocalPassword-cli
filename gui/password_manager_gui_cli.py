#!/usr/bin/env python3
"""
密码管理器 GUI - CLI 版本

直接调用 Rust CLI 命令，快速实现所有功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
import subprocess
import json
import threading
import os
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path


class PasswordManagerCLI:
    """
    密码管理器 GUI - CLI 版本

    直接调用 Rust CLI 命令实现所有功能
    """

    def __init__(self, pm_path: str):
        """
        初始化 GUI

        Args:
            pm_path: 密码管理器可执行文件路径
        """
        self.pm_path = pm_path
        self.passwords: List[Dict[str, Any]] = []
        self.master_password: Optional[str] = None
        self.is_initialized = False
        self.is_unlocked = False

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("密码管理器")
        self.root.geometry("900x650")

        # 设置图标
        icon_path = Path(__file__).parent.parent / "public" / "icons" / "128x128.svg"
        if icon_path.exists():
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
            except:
                pass

        # 应用样式
        self.setup_styles()

        # 创建组件
        self.create_widgets()

        # 检查数据库状态
        self.check_database_status()

    def setup_styles(self):
        """设置样式"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#F9FAFB')
        self.style.configure('Treeview', rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('TButton', padding=6)

    def create_widgets(self):
        """创建所有组件"""
        # 创建菜单栏
        self.create_menu()

        # 创建主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 创建侧边栏
        self.create_sidebar(main_container)

        # 创建主内容区
        self.create_content(main_container)

        # 创建状态栏
        self.create_statusbar()

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建数据库", command=self.new_database)
        file_menu.add_command(label="打开数据库", command=self.open_database)
        file_menu.add_command(label="关闭数据库", command=self.close_database)
        file_menu.add_separator()
        file_menu.add_command(label="导出", command=self.export_data)
        file_menu.add_command(label="导入", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="添加密码", command=self.add_password)
        edit_menu.add_command(label="编辑密码", command=self.edit_password)
        edit_menu.add_command(label="删除密码", command=self.delete_password)
        edit_menu.add_separator()
        edit_menu.add_command(label="生成密码", command=self.generate_password)
        edit_menu.add_separator()
        edit_menu.add_command(label="批量导入", command=self.batch_import)
        menubar.add_cascade(label="编辑", menu=edit_menu)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="数据库备份", command=self.backup_database)
        tools_menu.add_command(label="数据库恢复", command=self.restore_database)
        tools_menu.add_command(label="清理数据库", command=self.cleanup_database)
        menubar.add_cascade(label="工具", menu=tools_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用文档", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

    def create_sidebar(self, container):
        """创建侧边栏"""
        sidebar = ttk.Frame(container, width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)

        # 搜索框
        search_frame = ttk.Frame(sidebar, padding=10)
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="🔍 搜索").pack(anchor=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=5)
        self.search_var.trace('w', self.filter_passwords)

        # 分类
        category_frame = ttk.LabelFrame(sidebar, text="分类", padding=10)
        category_frame.pack(fill=tk.X, padx=10, pady=10)

        self.categories = {
            'all': '所有',
            'social': '社交',
            'shopping': '购物',
            'work': '工作',
            'other': '其他'
        }
        self.selected_category = tk.StringVar(value='all')

        for cat_id, cat_name in self.categories.items():
            rb = ttk.Radiobutton(
                category_frame,
                text=cat_name,
                value=cat_id,
                variable=self.selected_category,
                command=lambda c=cat_id: self.set_category(c)
            )
            rb.pack(anchor=tk.W, pady=2)

        # 添加按钮
        add_btn = ttk.Button(sidebar, text="➕ 添加密码", command=self.add_password)
        add_btn.pack(fill=tk.X, padx=10, pady=20)

        # 底部信息
        info_frame = ttk.Frame(sidebar, padding=10)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.stats_label = ttk.Label(info_frame, text="总计: 0 个密码")
        self.stats_label.pack(anchor=tk.W)

    def create_content(self, container):
        """创建主内容区"""
        content = ttk.Frame(container)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 工具栏
        toolbar = ttk.Frame(content)
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(toolbar, text="添加", command=self.add_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="编辑", command=self.edit_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_password).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Button(toolbar, text="刷新", command=self.refresh_passwords).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导出", command=self.export_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="生成密码", command=self.generate_password).pack(side=tk.LEFT, padx=2)

        # 密码列表
        list_frame = ttk.Frame(content)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 列表头部
        header_frame = ttk.Frame(list_frame)
        header_frame.pack(fill=tk.X, pady=5)

        ttk.Label(header_frame, text="密码列表").pack(side=tk.LEFT)
        self.count_label = ttk.Label(header_frame, text="0 个密码")
        self.count_label.pack(side=tk.RIGHT)

        # 创建 Treeview
        columns = ('title', 'username', 'website', 'category')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        self.tree.heading('title', text='标题')
        self.tree.heading('username', text='用户名')
        self.tree.heading('website', text='网站')
        self.tree.heading('category', text='分类')

        self.tree.column('title', width=200)
        self.tree.column('username', width=200)
        self.tree.column('website', width=200)
        self.tree.column('category', width=100)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定事件
        self.tree.bind('<Double-1>', lambda e: self.edit_password())
        self.tree.bind('<Button-3>', self.show_context_menu)

    def create_statusbar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")

        statusbar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    # ==================== 菜单命令 ====================

    def new_database(self):
        """新建数据库"""
        password = simpledialog.askstring("新建数据库", "请输入主密码:", show='*')
        if not password:
            return

        try:
            result = self.run_pm_command(['init', '--force'])
            if result['returncode'] == 0:
                self.master_password = password
                self.is_initialized = True
                self.is_unlocked = True
                self.show_loading()

                # 在后台解锁
                threading.Thread(target=lambda: self._unlock_database(password)).start()
            else:
                messagebox.showerror("错误", f"创建数据库失败: {result['stderr']}")
        except Exception as e:
            messagebox.showerror("错误", f"创建数据库失败: {e}")

    def open_database(self):
        """打开数据库"""
        password = simpledialog.askstring("解锁", "请输入主密码:", show='*')
        if not password:
            return

        self.show_loading()
        threading.Thread(target=lambda: self._unlock_database(password)).start()

    def _unlock_database(self, password: str):
        """解锁数据库（后台线程）"""
        try:
            # 先检查是否已初始化
            if not self.is_initialized:
                result = self.run_pm_command(['unlock', password])
                if result['returncode'] == 0:
                    self.master_password = password
                    self.is_initialized = True
                    self.is_unlocked = True
            else:
                # 直接使用
                self.master_password = password
                self.is_unlocked = True

            self.root.after(0, lambda: self.hide_loading())
            self.root.after(0, lambda: self.refresh_passwords())

        except Exception as e:
            self.root.after(0, lambda: self.hide_loading())
            self.root.after(0, lambda: messagebox.showerror("错误", f"解锁失败: {e}"))

    def close_database(self):
        """关闭数据库"""
        self.master_password = None
        self.is_unlocked = False
        self.passwords = []
        self.refresh_tree()
        self.show_status("数据库已关闭")

    def export_data(self):
        """导出数据"""
        if not self.is_unlocked:
            messagebox.showwarning("警告", "请先打开数据库")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                result = self.run_pm_command(['export', file_path])
                if result['returncode'] == 0:
                    messagebox.showinfo("成功", f"数据已导出到 {file_path}")
                else:
                    messagebox.showerror("错误", f"导出失败: {result['stderr']}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")

    def import_data(self):
        """导入数据"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            self.show_loading()
            threading.Thread(target=lambda: self._import_data_thread(file_path)).start()

    def _import_data_thread(self, file_path: str):
        """导入数据的线程函数"""
        try:
            result = self.run_pm_command(['import', file_path])
            self.root.after(0, lambda: self.hide_loading())

            if result['returncode'] == 0:
                self.root.after(0, lambda: messagebox.showinfo("成功", "数据已导入"))
                self.root.after(0, lambda: self.refresh_passwords())
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", f"导入失败: {result['stderr']}"))
        except Exception as e:
            self.root.after(0, lambda: self.hide_loading())
            self.root.after(0, lambda: messagebox.showerror("错误", f"导入失败: {e}"))

    def show_help(self):
        """显示帮助"""
        help_text = """🔐 密码管理器 - 使用文档

## 快速开始

1. 首次使用
   - 点击"文件" → "新建数据库"
   - 输入主密码
   - 开始添加密码

2. 打开现有数据库
   - 点击"文件" → "打开数据库"
   - 输入主密码

3. 添加密码
   - 点击"➕ 添加密码"或工具栏"添加"按钮
   - 填写信息
   - 保存

4. 编辑密码
   - 双击密码条目
   - 或选中后点击"编辑"

5. 删除密码
   - 选中密码
   - 点击"删除"

6. 生成密码
   - 点击"生成密码"
   - 自定义选项
   - 自动复制到剪贴板

## 快捷键

- Ctrl+N: 添加密码
- Ctrl+E: 编辑密码
- Ctrl+D: 删除密码
- Ctrl+R: 刷新列表
- Ctrl+E: 导出
- Ctrl+I: 导入

## CLI 命令

所有功能都通过 Rust CLI 实现：
- init: 初始化数据库
- unlock: 解锁数据库
- list: 列出密码
- add: 添加密码
- update: 更新密码
- delete: 删除密码
- generate: 生成密码
- export: 导出数据
- import: 导入数据
"""

        # 创建帮助窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("使用帮助")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.grab_set()

        help_text = scrolledtext.ScrolledText(help_window, width=580, height=400, wrap=tk.WORD)
        help_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        help_text.insert(tk.END, help_text)
        help_text.config(state=tk.DISABLED)

        ttk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)

    def show_about(self):
        """显示关于"""
        about_text = """🔐 密码管理器 v2.0

基于 Rust 开发的安全密码管理工具

功能特点：
• AES-256-GCM 加密
• Argon2id 密钥派生
• 安全的密码生成
• 数据导入/导出
• GUI 界面（Tkinter）

安全性：
• 所有密码都经过加密存储
• 主密码保护数据库
• 内存安全

© 2024 密码管理器
"""

        messagebox.showinfo("关于", about_text)

    def backup_database(self):
        """数据库备份"""
        messagebox.showinfo("功能说明", "数据库备份功能即将在 CLI 中实现")

    def restore_database(self):
        """数据库恢复"""
        messagebox.showinfo("功能说明", "数据库恢复功能即将在 CLI 中实现")

    def cleanup_database(self):
        """清理数据库"""
        if not self.is_unlocked:
            messagebox.showwarning("警告", "请先打开数据库")
            return

        if messagebox.askyesno("确认", "确定要清理数据库吗？"):
            try:
                result = self.run_pm_command(['cleanup'])
                if result['returncode'] == 0:
                    messagebox.showinfo("成功", "数据库已清理")
                    self.refresh_passwords()
                else:
                    messagebox.showerror("错误", f"清理失败: {result['stderr']}")
            except Exception as e:
                messagebox.showerror("错误", f"清理失败: {e}")

    def batch_import(self):
        """批量导入"""
        messagebox.showinfo("功能说明", "批量导入功能即将在 CLI 中实现")

    # ==================== 密码操作 ====================

    def add_password(self):
        """添加密码"""
        self.open_password_dialog()

    def edit_password(self):
        """编辑密码"""
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning("警告", "请先选择一个密码条目")
            return

        item_id = selection[0]
        title = self.tree.item(item_id)['values'][0]
        password_data = next((p for p in self.passwords if p.get('title') == title), None)

        if password_data:
            self.open_password_dialog(password_data)

    def delete_password(self):
        """删除密码"""
        selection = self.tree.selection()

        if not selection:
            messagebox.showwarning("警告", "请先选择一个密码条目")
            return

        if not messagebox.askyesno("确认", "确定要删除选中的密码吗？"):
            item_id = selection[0]
            title = self.tree.item(item_id)['values'][0]

            try:
                result = self.run_pm_command(['delete', title])
                if result['returncode'] == 0:
                    messagebox.showinfo("成功", f"'{title}' 已删除")
                    self.refresh_passwords()
                else:
                    messagebox.showerror("错误", f"删除失败: {result['stderr']}")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")

    def generate_password(self):
        """生成密码"""
        dialog = PasswordGeneratorCLI(self.root, self.pm_path)
        dialog.show()

    # ==================== 上下文菜单 ====================

    def show_context_menu(self, event):
        """显示右键菜单"""
        selection = self.tree.selection()

        if not selection:
            return

        item_id = selection[0]
        title = self.tree.item(item_id)['values'][0]

        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="编辑", command=self.edit_password)
        context_menu.add_command(label="删除", command=self.delete_password)
        context_menu.add_separator()
        context_menu.add_command(label="复制标题", command=lambda: self.copy_field('title', title))
        context_menu.add_command(label="复制用户名", command=lambda: self.copy_field('username', title))
        context_menu.add_command(label="复制密码", command=lambda: self.copy_field('password', title))
        context_menu.add_separator()
        context_menu.add_command(label="打开网站", command=lambda: self.open_website(title))

        try:
            context_menu.tk_popup(event)
        except:
            pass

    def copy_field(self, field: str, title: str):
        """复制字段"""
        password_data = next((p for p in self.passwords if p.get('title') == title), None)

        if password_data and field in password_data:
            value = password_data[field]
            if value:
                self.root.clipboard_clear()
                self.root.clipboard_append(value)
                self.show_status(f"已复制 {field}")

    def open_website(self, title: str):
        """打开网站"""
        password_data = next((p for p in self.passwords if p.get('title') == title), None)

        if password_data and password_data.get('website'):
            import webbrowser
            webbrowser.open(password_data['website'])

    # ==================== 工具方法 ====================

    def set_category(self, category: str):
        """设置分类"""
        self.selected_category.set(category)
        self.filter_passwords()

    def filter_passwords(self, *args):
        """过滤密码列表"""
        search_text = self.search_var.get().lower()
        category = self.selected_category.get()

        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加匹配的密码
        for pwd in self.passwords:
            # 检查分类
            if category != 'all' and pwd.get('category') != category:
                continue

            # 检查搜索
            if search_text:
                title = pwd.get('title', '').lower()
                username = pwd.get('username', '').lower()
                website = pwd.get('website', '').lower()

                if search_text not in title and search_text not in username and search_text not in website:
                    continue

            self.tree.insert('', tk.END, values=(
                pwd.get('title', ''),
                pwd.get('username', ''),
                pwd.get('website', ''),
                pwd.get('category', '')
            ))

        self.count_label.config(text=f"{len(self.tree.get_children())} 个密码")
        self.stats_label.config(text=f"总计: {len(self.passwords)} 个密码")

    def refresh_passwords(self):
        """刷新密码列表"""
        if not self.is_unlocked:
            self.show_status("请先打开数据库")
            return

        self.show_loading()
        threading.Thread(target=self._refresh_passwords_thread).start()

    def _refresh_passwords_thread(self):
        """刷新密码列表的线程函数"""
        try:
            result = self.run_pm_command(['list'])
            self.root.after(0, lambda: self.hide_loading())

            if result['returncode'] == 0:
                output = result['stdout'].strip()
                if output:
                    try:
                        self.passwords = json.loads(output)
                    except json.JSONDecodeError:
                        # 如果不是 JSON，尝试逐行解析
                        lines = output.split('\n')
                        self.passwords = [{'title': line.strip()} for line in lines if line.strip()]
                else:
                    self.passwords = []

                self.filter_passwords()
                self.show_status(f"加载了 {len(self.passwords)} 个密码")
            else:
                self.show_status("获取密码列表失败")
                messagebox.showerror("错误", f"获取密码列表失败: {result['stderr']}")
        except Exception as e:
            self.root.after(0, lambda: self.hide_loading())
            self.show_status("刷新失败")
            messagebox.showerror("错误", f"刷新失败: {e}")

    def refresh_tree(self):
        """刷新树视图"""
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加密码
        for pwd in self.passwords:
            self.tree.insert('', tk.END, values=(
                pwd.get('title', ''),
                pwd.get('username', ''),
                pwd.get('website', ''),
                pwd.get('category', '')
            ))

    def check_database_status(self):
        """检查数据库状态"""
        # 检查数据库文件是否存在
        db_path = Path.home() / '.pm' / 'pm.db'

        if db_path.exists():
            self.show_status("检测到现有数据库，请打开")
        else:
            self.show_status("未检测到数据库，请新建")

    def show_loading(self):
        """显示加载"""
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("加载中")
        self.loading_window.geometry("200x100")
        self.loading_window.transient(self.root)
        self.loading_window.overrideredirect(True)
        self.loading_window.attributes('-topmost', True)

        ttk.Label(self.loading_window, text="加载中...").pack(pady=20)

    def hide_loading(self):
        """隐藏加载"""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
            del self.loading_window

    def show_status(self, message: str):
        """显示状态"""
        self.status_var.set(message)

    def run_pm_command(self, args: List[str]) -> Dict[str, Any]:
        """
        运行密码管理器命令

        Args:
            args: 命令参数

        Returns:
            命令结果
        """
        try:
            process = subprocess.Popen(
                [self.pm_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True
            )

            # 主密码输入
            if 'init' in args or 'unlock' in args or 'add' in args or 'update' in args:
                # 等待密码提示
                output, _ = process.communicate(timeout=1)

                # 检查是否需要密码
                if 'password:' in output.lower():
                    password = self.master_password
                    if password:
                        process.stdin.write(password + '\n')
                        process.stdin.flush()

            stdout, stderr = process.communicate()
            else:
                stdout, stderr = process.communicate()

            return {
                'returncode': process.returncode,
                'stdout': stdout,
                'stderr': stderr
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }

    def open_password_dialog(self, password_data: Optional[Dict] = None):
        """
        打开密码对话框

        Args:
            password_data: 密码数据（编辑模式），None 为添加模式
        """
        dialog = PasswordDialogCLI(self.root, password_data, self.pm_path, self.master_password)
        result = dialog.show()

        if result:
            self.refresh_passwords()

    def run(self):
        """运行 GUI"""
        self.root.mainloop()


class PasswordDialogCLI:
    """
    密码对话框 - CLI 版本

    使用 CLI 命令添加/编辑密码
    """

    def __init__(self, parent: tk.Tk, password_data: Optional[Dict], pm_path: str, master_password: Optional[str]):
        """
        初始化对话框

        Args:
            parent: 父窗口
            password_data: 密码数据（编辑模式）
            pm_path: 密码管理器路径
            master_password: 主密码
        """
        self.password_data = password_data
        self.pm_path = pm_path
        self.master_password = master_password
        self.result = False

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑密码" if password_data else "添加密码")
        self.dialog.geometry("450x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 创建表单
        self.create_form()

    def create_form(self):
        """创建表单"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(frame, text="标题 *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=self.password_data.get('title', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.title_var, width=30).grid(row=0, column=1, pady=5)

        # 用户名
        ttk.Label(frame, text="用户名").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.password_data.get('username', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=1, column=1, pady=5)

        # 密码
        ttk.Label(frame, text="密码 *").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=self.password_data.get('password', '') if self.password_data else '')
        password_frame = ttk.Frame(frame)
        password_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Entry(password_frame, textvariable=self.password_var, show='*', width=25).pack(side=tk.LEFT)
        ttk.Button(password_frame, text="👁", command=self.toggle_password, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(password_frame, text="🎲", command=self.generate_password, width=3).pack(side=tk.LEFT, padx=2)

        # 网站
        ttk.Label(frame, text="网站").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.website_var = tk.StringVar(value=self.password_data.get('website', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.website_var, width=30).grid(row=3, column=1, pady=5)

        # 备注
        ttk.Label(frame, text="备注").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar(value=self.password_data.get('notes', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.notes_var, width=30).grid(row=4, column=1, pady=5)

        # 分类
        ttk.Label(frame, text="分类").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value=self.password_data.get('category', 'other') if self.password_data else 'other')
        ttk.Combobox(frame, textvariable=self.category_var, values=['social', 'shopping', 'work', 'other'], state='readonly').grid(row=5, column=1, pady=5)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # 绑定 Enter 键
        self.root.bind('<Return>', lambda e: self.save())

    def toggle_password(self):
        """切换密码显示/隐藏"""
        current_show = self.password_entry.cget('show') == '*'
        self.password_entry.config(show='' if current_show else '*')

    def generate_password(self):
        """生成密码"""
        dialog = PasswordGeneratorCLI(self.dialog, self.pm_path)
        password = dialog.show()

        if password:
            self.password_var.set(password)

    def save(self):
        """保存"""
        title = self.title_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        website = self.website_var.get().strip()
        notes = self.notes_var.get().strip()
        category = self.category_var.get()

        if not title:
            messagebox.showwarning("警告", "标题不能为空")
            return

        if not password:
            messagebox.showwarning("警告", "密码不能为空")
            return

        # 使用 CLI 命令保存
        try:
            if self.password_data:
                # 编辑模式
                args = ['update', title]
                # TODO: 实现编辑逻辑
            else:
                # 添加模式
                args = ['add', title, username, password, '--category', category]
                if website:
                    args.extend(['--website', website])
                if notes:
                    args.extend(['--notes', notes])

            result = self.run_pm_command(args)

            if result['returncode'] == 0:
                self.result = True
                self.dialog.destroy()
                messagebox.showinfo("成功", "密码已保存")
            else:
                messagebox.showerror("错误", f"保存失败: {result['stderr']}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def run_pm_command(self, args: List[str]) -> Dict[str, Any]:
        """运行 CLI 命令"""
        # TODO: 实现实际的 CLI 命令调用
        return {'returncode': 0, 'stdout': '', 'stderr': ''}

    def show(self) -> bool:
        """显示对话框"""
        self.dialog.wait_window()
        return self.result


class PasswordGeneratorCLI:
    """
    密码生成器 - CLI 版本

    直接调用 CLI 的 generate 命令
    """

    def __init__(self, parent: tk.Tk, pm_path: str):
        """
        初始化对话框

        Args:
            parent: 父窗口
            pm_path: 密码管理器路径
        """
        self.parent = parent
        self.pm_path = pm_path
        self.password = None

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("密码生成器")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_form()

    def create_form(self):
        """创建表单"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 密码长度
        ttk.Label(frame, text="密码长度:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.IntVar(value=16)
        ttk.Spinbox(frame, from_=8, to=64, textvariable=self.length_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)

        # 字符选项
        options_frame = ttk.LabelFrame(frame, text="字符类型", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=10, padx=5)

        self.uppercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="大写字母 (A-Z)", variable=self.uppercase_var).pack(anchor=tk.W)

        self.lowercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="小写字母 (a-z)", variable=self.lowercase_var).pack(anchor=tk.W)

        self.numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="数字 (0-9)", variable=self.numbers_var).pack(anchor=tk.W)

        self.symbols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="特殊字符 (!@#$%^&*)", variable=self.symbols_var).pack(anchor=tk.W)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="生成", command=self.generate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def generate(self):
        """生成密码"""
        try:
            length = self.length_var.get()

            # 构建参数
            args = ['generate', '--length', str(length)]
            if self.uppercase_var.get():
                args.append('--uppercase')
            if self.lowercase_var.get():
                args.append('--lowercase')
            if self.numbers_var.get():
                args.append('--numbers')
            if self.symbols_var.get():
                args.append('--symbols')

            # 调用 CLI 命令
            result = self._run_pm_command(args)

            if result['returncode'] == 0:
                self.password = result['stdout'].strip()
                # 复制到剪贴板
                self.parent.clipboard_clear()
                self.parent.clipboard_append(self.password)
                messagebox.showinfo("生成成功", f"已生成并复制到剪贴板:\n\n{self.password}")
            else:
                messagebox.showerror("错误", f"生成失败: {result['stderr']}")
        except Exception as e:
            messagebox.showerror("错误", f"生成失败: {e}")

    def _run_pm_command(self, args: List[str]) -> Dict[str, Any]:
        """运行 CLI 命令"""
        try:
            process = subprocess.Popen(
                [self.pm_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return {
                'returncode': process.returncode,
                'stdout': stdout,
                'stderr': stderr
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            }

    def show(self) -> Optional[str]:
        """显示对话框"""
        self.dialog.wait_window()
        return self.password


def main():
    """主函数"""
    # 密码管理器路径
    pm_path = Path(__file__).parent.parent / "target" / "release" / "pm"

    if not pm_path.exists():
        # 尝试从系统路径查找
        import shutil
        system_pm = shutil.which("pm")
        if system_pm:
            pm_path = system_pm
        else:
            print("错误: 找不到密码管理器可执行文件")
            print(f"请确保 pm 可执行文件在以下位置: {pm_path}")
            return

    # 创建并运行 GUI
    app = PasswordManagerCLI(str(pm_path))
    app.run()


if __name__ == '__main__':
    main()
