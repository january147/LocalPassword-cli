#!/usr/bin/env python3
"""
密码管理器 GUI 界面 - 增强版

集成所有新功能：
- 欢迎页面
- 主题管理
- Toast 通知
- 密码强度可视化
- 加载动画
- 设置对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import json
import os
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
import threading

# 导入自定义模块
from welcome_page import WelcomePage, show_welcome_dialog
from settings_dialog import SettingsDialog
from toast_manager import ToastManager
from theme_manager import ThemeManager
from password_strength import PasswordStrengthAnalyzer


class PasswordManagerGUI:
    """
    密码管理器 GUI - 增强版

    新功能：
    - 欢迎页面（首次启动）
    - 主题切换（亮色/暗色）
    - Toast 通知
    - 密码强度可视化
    - 加载动画
    - 设置对话框
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
        self.settings: Dict[str, Any] = {
            'theme': 'light',
            'font_size': 10,
            'auto_lock': '5min',
            'clipboard': 'immediate',
            'db_path': '~/.pm/pm.db',
            'check_strength': True,
            'check_duplicates': True
        }

        # 初始化管理器
        self.theme_manager = ThemeManager()
        self.toast_manager = ToastManager(self.root)
        self.strength_analyzer = PasswordStrengthAnalyzer()

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("密码管理器")
        self.root.geometry("900x650")

        # 设置窗口图标
        icon_path = Path(__file__).parent.parent / "public" / "icons" / "128x128.svg"
        if icon_path.exists():
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=str(icon_path)))
            except:
                pass

        # 应用主题
        self.apply_theme()

        # 创建组件
        self.create_widgets()

        # 检查是否需要显示欢迎页面
        self.check_first_run()

    def create_widgets(self):
        """创建所有组件"""
        # 创建菜单栏
        self.create_menu()

        # 创建工具栏
        self.create_toolbar()

        # 创建搜索框
        self.create_search()

        # 创建密码列表
        self.create_password_list()

        # 创建状态栏
        self.create_statusbar()

        # 创建加载动画
        self.create_loading()

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
        file_menu.add_command(label="设置", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="切换主题", command=self.toggle_theme)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="添加", command=self.add_password)
        edit_menu.add_command(label="编辑", command=self.edit_password)
        edit_menu.add_command(label="删除", command=self.delete_password)
        edit_menu.add_separator()
        edit_menu.add_command(label="生成密码", command=self.generate_password)
        menubar.add_cascade(label="编辑", menu=edit_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # 添加按钮
        ttk.Button(toolbar, text="添加", command=self.add_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="编辑", command=self.edit_password).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_password).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="刷新", command=self.refresh_passwords).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="生成密码", command=self.generate_password).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # 主题切换按钮
        theme_btn = ttk.Button(toolbar, text="切换主题", command=self.toggle_theme)
        theme_btn.pack(side=tk.LEFT, padx=2)

        # 设置按钮
        ttk.Button(toolbar, text="设置", command=self.open_settings).pack(side=tk.LEFT, padx=2)

    def create_search(self):
        """创建搜索框"""
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_passwords)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # 清除按钮
        ttk.Button(search_frame, text="×", command=self.clear_search, width=3).pack(side=tk.LEFT, padx=2)

    def create_password_list(self):
        """创建密码列表"""
        # 创建 Treeview
        columns = ('title', 'username', 'website', 'strength')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')

        # 设置列
        self.tree.heading('title', text='标题')
        self.tree.heading('username', text='用户名')
        self.tree.heading('website', text='网站')
        self.tree.heading('strength', text='强度')

        self.tree.column('title', width=200)
        self.tree.column('username', width=200)
        self.tree.column('website', width=200)
        self.tree.column('strength', width=80)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # 绑定双击事件
        self.tree.bind('<Double-1>', lambda e: self.edit_password())

        # 绑定右键菜单
        self.tree.bind('<Button-3>', self.show_context_menu)

    def create_statusbar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.BOTTOM, fill=tk.X)

    def create_loading(self):
        """创建加载动画"""
        self.loading_frame = tk.Frame(self.root)
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 加载图标
        self.loading_label = tk.Label(self.loading_frame, text="加载中...", font=('Arial', 14))
        self.loading_label.pack()

        # 旋转动画（简化版）
        self.loading_dots = 0
        self.loading_label.config(text="加载中.")

        # 隐藏加载动画
        self.loading_frame.place_forget()

    def show_loading(self):
        """显示加载动画"""
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.loading_dots = 0
        self.animate_loading()

    def hide_loading(self):
        """隐藏加载动画"""
        self.loading_frame.place_forget()

    def animate_loading(self):
        """加载动画"""
        if self.loading_frame.winfo_ismapped():
            self.loading_dots = (self.loading_dots + 1) % 4
            dots = "." * self.loading_dots
            self.loading_label.config(text=f"加载中{dots}")
            self.root.after(500, self.animate_loading)

    def apply_theme(self):
        """应用当前主题"""
        theme = self.theme_manager.get_theme(self.settings['theme'])

        # 应用到样式
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 配置 Treeview
        self.style.configure('Treeview', rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('Treeview.Heading', background=theme['card_bg'], foreground=theme['card_fg'])

        # 应用到窗口
        self.root.configure(bg=theme['bg'])

        # 应用到 Treeview
        self.tree.configure(style='Treeview')

    def toggle_theme(self):
        """切换主题"""
        new_theme = self.theme_manager.toggle_theme(self.root, self.style)
        self.settings['theme'] = new_theme

        # 显示 Toast
        self.toast_manager.info(f"已切换到 {self.theme_manager.get_available_themes()[new_theme]}")

    def check_first_run(self):
        """检查是否首次运行"""
        # 检查数据库文件是否存在
        db_path = Path(os.path.expanduser(self.settings['db_path']))

        if not db_path.exists():
            # 显示欢迎页面
            show_welcome_dialog(
                self.root,
                on_init=lambda: self.init_database(),
                on_import=lambda path: self.import_database(path)
            )
        else:
            # 显示数据库解锁对话框
            password = simpledialog.askstring("解锁", "请输入主密码:", show='*')
            if password:
                self.master_password = password
                self.refresh_passwords()

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 获取选中的项目
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        title = self.tree.item(item_id)['values'][0]

        # 创建右键菜单
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="编辑", command=self.edit_password)
        context_menu.add_command(label="删除", command=self.delete_password)
        context_menu.add_separator()
        context_menu.add_command(label="复制用户名", command=lambda: self.copy_field(item_id, 'username'))
        context_menu.add_command(label="复制密码", command=lambda: self.copy_field(item_id, 'password'))
        context_menu.add_separator()
        context_menu.add_command(label="打开网站", command=lambda: self.open_website(item_id))

        # 显示菜单
        try:
            context_menu.tk_popup(event)
        except:
            pass

    # ==================== 菜单命令 ====================

    def new_database(self):
        """新建数据库"""
        self.toast_manager.info("创建新数据库...")
        # TODO: 实现新建数据库
        messagebox.showinfo("功能开发中", "此功能正在开发中")

    def open_database(self):
        """打开数据库"""
        password = simpledialog.askstring("打开数据库", "请输入主密码:", show='*')
        if password:
            self.master_password = password
            self.refresh_passwords()

    def close_database(self):
        """关闭数据库"""
        self.master_password = None
        self.passwords = []
        self.refresh_tree()
        self.toast_manager.info("数据库已关闭")

    def export_data(self):
        """导出数据"""
        if not self.master_password:
            self.toast_manager.warning("请先打开数据库")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                result = self.run_pm_command(['export', file_path])
                if result['returncode'] == 0:
                    self.toast_manager.success(f"数据已导出到 {file_path}")
                else:
                    self.toast_manager.error(f"导出失败: {result['stderr']}")
            except Exception as e:
                self.toast_manager.error(f"导出失败: {e}")

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
                self.root.after(0, lambda: self.toast_manager.success("数据已导入"))
                self.root.after(0, lambda: self.refresh_passwords())
            else:
                self.root.after(0, lambda: self.toast_manager.error(f"导入失败: {result['stderr']}"))
        except Exception as e:
            self.root.after(0, lambda: self.hide_loading())
            self.root.after(0, lambda: self.toast_manager.error(f"导入失败: {e}"))

    def open_settings(self):
        """打开设置"""
        dialog = SettingsDialog(self.root, self.settings)
        new_settings = dialog.show()

        if new_settings:
            self.settings = new_settings
            self.apply_theme()
            self.toast_manager.success("设置已保存")

    def show_about(self):
        """显示关于"""
        about_text = """🔐 密码管理器 v2.0

基于 Rust 开发的安全密码管理工具

新功能：
• 欢迎页面
• 主题切换（亮色/暗色）
• Toast 通知
• 密码强度可视化
• 加载动画
• 设置对话框

安全性：
• AES-256-GCM 加密
• Argon2id 密钥派生
• 安全的密码生成

© 2024 密码管理器
        """

        messagebox.showinfo("关于", about_text)

    # ==================== 密码操作 ====================

    def add_password(self):
        """添加密码"""
        self.open_password_dialog()

    def edit_password(self):
        """编辑密码"""
        selection = self.tree.selection()

        if not selection:
            self.toast_manager.warning("请先选择一个密码条目")
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
            self.toast_manager.warning("请先选择一个密码条目")
            return

        item_id = selection[0]
        title = self.tree.item(item_id)['values'][0]

        if messagebox.askyesno("确认", f"确定要删除 '{title}' 吗？"):
            try:
                result = self.run_pm_command(['delete', title])
                if result['returncode'] == 0:
                    self.toast_manager.success(f"'{title}' 已删除")
                    self.refresh_passwords()
                else:
                    self.toast_manager.error(f"删除失败: {result['stderr']}")
            except Exception as e:
                self.toast_manager.error(f"删除失败: {e}")

    def generate_password(self):
        """生成密码"""
        # 打开密码生成器对话框
        dialog = PasswordGeneratorDialog(self.root)
        password = dialog.show()

        if password:
            # 分析密码强度
            strength_info = self.strength_analyzer.analyze(password)

            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(password)

            # 显示 Toast
            self.toast_manager.success(
                f"已生成 {strength_info['level']} 密码并复制到剪贴板"
            )

    def copy_field(self, item_id: str, field: str):
        """复制字段"""
        title = self.tree.item(item_id)['values'][0]
        password_data = next((p for p in self.passwords if p.get('title') == title), None)

        if password_data:
            value = password_data.get(field, '')
            if value:
                self.root.clipboard_clear()
                self.root.clipboard_append(value)
                self.toast_manager.success(f"已复制 {field}")

    def open_website(self, item_id: str):
        """打开网站"""
        title = self.tree.item(item_id)['values'][0]
        password_data = next((p for p in self.passwords if p.get('title') == title), None)

        if password_data and password_data.get('website'):
            try:
                import webbrowser
                webbrowser.open(password_data['website'])
            except Exception as e:
                self.toast_manager.error(f"打开网站失败: {e}")

    def clear_search(self):
        """清除搜索"""
        self.search_var.set('')
        self.filter_passwords()

    # ==================== 密码对话框 ====================

    def open_password_dialog(self, password_data: Optional[Dict] = None):
        """
        打开密码对话框

        Args:
            password_data: 密码数据（编辑模式），None 为添加模式
        """
        dialog = PasswordDialog(self.root, password_data, self.pm_path, self.master_password)
        result = dialog.show()

        if result:
            self.toast_manager.success("密码已保存")
            self.refresh_passwords()

    # ==================== 工具方法 ====================

    def refresh_passwords(self):
        """刷新密码列表"""
        self.show_loading()
        threading.Thread(target=self._refresh_passwords_thread).start()

    def _refresh_passwords_thread(self):
        """刷新密码列表的线程函数"""
        try:
            result = self.run_pm_command(['list'])
            self.root.after(0, lambda: self.hide_loading())

            if result['returncode'] == 0:
                # 解析输出
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

                self.root.after(0, lambda: self.refresh_tree())
                self.root.after(0, lambda: self.status_var.set(f"共 {len(self.passwords)} 个密码"))
            else:
                self.root.after(0, lambda: self.toast_manager.error(f"获取密码列表失败: {result['stderr']}"))
        except Exception as e:
            self.root.after(0, lambda: self.hide_loading())
            self.root.after(0, lambda: self.toast_manager.error(f"刷新失败: {e}"))

    def refresh_tree(self):
        """刷新树视图"""
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加密码
        theme = self.theme_manager.get_theme(self.settings['theme'])

        for pwd in self.passwords:
            # 分析密码强度
            password = pwd.get('password', '')
            strength_info = self.strength_analyzer.analyze(password)

            # 根据强度设置颜色标签
            if strength_info['strength'] == 'very_strong':
                strength_color = '#10B981'  # green
            elif strength_info['strength'] == 'strong':
                strength_color = '#22C55E'  # blue
            elif strength_info['strength'] == 'medium':
                strength_color = '#F59E0B'  # orange
            else:
                strength_color = '#EF4444'  # red

            # 强度标签
            strength_tag = f"🔐 {strength_info['level']}"

            self.tree.insert('', tk.END, values=(
                pwd.get('title', ''),
                pwd.get('username', ''),
                pwd.get('website', ''),
                strength_tag
            ))

            # 设置行颜色（如果支持）
            # self.tree.tag_configure(row_id, background=strength_info['color'])

    def filter_passwords(self, *args):
        """过滤密码列表"""
        search_text = self.search_var.get().lower()

        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 添加匹配的密码
        for pwd in self.passwords:
            title = pwd.get('title', '').lower()
            username = pwd.get('username', '').lower()
            website = pwd.get('website', '').lower()

            if search_text in title or search_text in username or search_text in website:
                password = pwd.get('password', '')
                strength_info = self.strength_analyzer.analyze(password)

                strength_tag = f"🔐 {strength_info['level']}"

                self.tree.insert('', tk.END, values=(
                    pwd.get('title', ''),
                    pwd.get('username', ''),
                    pwd.get('website', ''),
                    strength_tag
                ))

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

    def run(self):
        """运行 GUI"""
        self.root.mainloop()


class PasswordDialog:
    """
    密码对话框 - 增强版
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

        # 初始化分析器
        self.strength_analyzer = PasswordStrengthAnalyzer()

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑密码" if password_data else "添加密码")
        self.dialog.geometry("500x600")
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
        title_entry = ttk.Entry(frame, textvariable=self.title_var, width=30)
        title_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        title_entry.focus_set()

        # 绑定 Enter 键
        title_entry.bind('<Return>', lambda e: self.focus_next())

        # 用户名
        ttk.Label(frame, text="用户名").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar(value=self.password_data.get('username', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.username_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 密码
        ttk.Label(frame, text="密码 *").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar(value=self.password_data.get('password', '') if self.password_data else '')

        password_frame = ttk.Frame(frame)
        password_frame.grid(row=2, column=1, sticky=tk.W, pady=5)

        ttk.Entry(password_frame, textvariable=self.password_var, show='*', width=25).pack(side=tk.LEFT)

        # 密码强度条
        self.strength_bar = tk.Canvas(password_frame, width=200, height=8, bg='#E5E7EB', highlightthickness=0)
        self.strength_bar.pack(side=tk.LEFT, padx=10)

        # 强度显示
        ttk.Button(password_frame, text="👁", command=self.toggle_password, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(password_frame, text="🎲", command=self.generate_new_password, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(password_frame, text="生成密码", command=self.open_generator).pack(side=tk.LEFT, padx=5)

        # 强度文本
        self.strength_label = ttk.Label(frame, text="密码强度: 未设置", grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 网址
        ttk.Label(frame, text="网站").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.website_var = tk.StringVar(value=self.password_data.get('website', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.website_var, width=30).grid(row=4, column=1, sticky=tk.W, pady=5)

        # 备注
        ttk.Label(frame, text="备注").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar(value=self.password_data.get('notes', '') if self.password_data else '')
        ttk.Entry(frame, textvariable=self.notes_var, width=30).grid(row=5, column=1, sticky=tk.W, pady=5)

        # 分类
        ttk.Label(frame, text="分类").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value=self.password_data.get('category', 'other') if self.password_data else 'other')
        category_combo = ttk.Combobox(frame, textvariable=self.category_var, values=['social', 'shopping', 'work', 'other'], state='readonly')
        category_combo.grid(row=6, column=1, sticky=tk.W, pady=5)

        # 绑定密码变化事件
        self.password_var.trace('w', lambda *args: self.update_strength())

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def update_strength(self):
        """更新密码强度显示"""
        password = self.password_var.get()
        if not password:
            self.strength_bar.delete('all')
            self.strength_label.config(text="密码强度: 未设置")
            return

        # 分析密码强度
        strength_info = self.strength_analyzer.analyze(password)

        # 绘制强度条
        self.strength_bar.delete('all')
        self.draw_strength_bar(strength_info['bar_width'], strength_info['color'])

        # 更新标签
        self.strength_label.config(text=f"密码强度: {strength_info['level']}")

    def draw_strength_bar(self, width: int, color: str):
        """绘制强度条"""
        if width > 0:
            self.strength_bar.create_rectangle(0, 0, width, 8, fill=color, outline='')
        self.strength_bar.create_rectangle(width, 0, 200-width, 8, fill='#E5E7EB', outline='')

    def toggle_password(self):
        """切换密码显示/隐藏"""
        current_show = self.password_entry.cget('show') == '*'
        self.password_entry.config(show='' if current_show else '*')

    def generate_new_password(self):
        """生成新密码"""
        import random
        import string

        length = 16
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        password = ''.join(random.choice(chars) for _ in range(length))

        self.password_var.set(password)

    def open_generator(self):
        """打开密码生成器对话框"""
        dialog = PasswordGeneratorDialog(self.dialog)
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

        # TODO: 调用密码管理器保存密码
        # 由于 CLI 交互复杂，这里先模拟

        self.result = True
        self.dialog.destroy()

    def show(self) -> bool:
        """显示对话框"""
        self.dialog.wait_window()
        return self.result

    def focus_next(self):
        """焦点移动到下一个控件"""
        self.dialog.focus_set()
        # TODO: 实现焦点移动


class PasswordGeneratorDialog:
    """
    密码生成器对话框
    """

    def __init__(self, parent: tk.Tk):
        """
        初始化对话框

        Args:
            parent: 父窗口
        """
        self.password = None

        # 初始化分析器
        self.strength_analyzer = PasswordStrengthAnalyzer()

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("密码生成器")
        self.dialog.geometry("400x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 创建表单
        self.create_form()

    def create_form(self):
        """创建表单"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 生成的密码
        ttk.Label(frame, text="生成的密码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.generated_password_var = tk.StringVar()

        password_frame = ttk.Frame(frame)
        password_frame.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Entry(password_frame, textvariable=self.generated_password_var, width=25).pack(side=tk.LEFT)
        ttk.Button(password_frame, text="复制", command=self.copy_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(password_frame, text="重新生成", command=self.generate).pack(side=tk.LEFT, padx=5)

        # 密码长度
        ttk.Label(frame, text="密码长度:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.IntVar(value=16)
        ttk.Spinbox(frame, from_=8, to=64, textvariable=self.length_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 字符选项
        options_frame = ttk.LabelFrame(frame, text="字符类型", padding="10")
        options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10, padx=5)

        self.uppercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="大写字母 (A-Z)", variable=self.uppercase_var).pack(anchor=tk.W)

        self.lowercase_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="小写字母 (a-z)", variable=self.lowercase_var).pack(anchor=tk.W)

        self.numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="数字 (0-9)", variable=self.numbers_var).pack(anchor=tk.W)

        self.symbols_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="特殊字符 (!@#$%^&*)", variable=self.symbols_var).pack(anchor=tk.W)

        # 强度显示
        self.strength_label = ttk.Label(frame, text="密码强度: 未生成", grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)

        # 强度条
        self.strength_bar = tk.Canvas(frame, width=300, height=10, bg='#E5E7EB', highlightthickness=0)
        self.strength_bar.grid(row=4, column=0, columnspan=2, sticky=tk.W)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="确定", command=self.ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # 绑定生成按钮事件
        self.generated_password_var.trace('w', lambda *args: self.update_strength())

    def generate(self):
        """生成密码"""
        import random
        import string

        length = self.length_var.get()

        chars = ""
        if self.uppercase_var.get():
            chars += string.ascii_uppercase
        if self.lowercase_var.get():
            chars += string.ascii_lowercase
        if self.numbers_var.get():
            chars += string.digits
        if self.symbols_var.get():
            chars += "!@#$%^&*"

        if not chars:
            messagebox.showwarning("警告", "请至少选择一种字符类型")
            return

        self.password = ''.join(random.choice(chars) for _ in range(length))
        self.generated_password_var.set(self.password)

    def update_strength(self):
        """更新密码强度显示"""
        password = self.generated_password_var.get()
        if not password:
            self.strength_bar.delete('all')
            self.strength_label.config(text="密码强度: 未生成")
            return

        # 分析密码强度
        strength_info = self.strength_analyzer.analyze(password)

        # 绘制强度条
        self.strength_bar.delete('all')
        if strength_info['bar_width'] > 0:
            self.strength_bar.create_rectangle(0, 0, strength_info['bar_width'] * 3, 10, fill=strength_info['color'], outline='')
            self.strength_bar.create_rectangle(strength_info['bar_width'] * 3, 0, 300 - strength_info['bar_width'] * 3, 10, fill='#E5E7EB', outline='')

        # 更新标签
        self.strength_label.config(text=f"密码强度: {strength_info['level']}")

    def copy_password(self):
        """复制密码到剪贴板"""
        password = self.generated_password_var.get()
        if password:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(password)
            messagebox.showinfo("已复制", "密码已复制到剪贴板")

    def ok(self):
        """确定"""
        if self.password:
            self.dialog.destroy()

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
    app = PasswordManagerGUI(str(pm_path))
    app.run()


if __name__ == '__main__':
    main()
