#!/usr/bin/env python3
"""
设置对话框
"""

import tkinter as tk
from tkinter import ttk


class SettingsDialog:
    """
    设置对话框
    """

    def __init__(self, parent: tk.Tk, settings: dict):
        """
        初始化对话框

        Args:
            parent: 父窗口
            settings: 当前设置
        """
        self.settings = settings
        self.result = False
        self.new_settings = settings.copy()

        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 创建表单
        self.create_form()

    def create_form(self):
        """创建表单"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 外观设置
        appearance_frame = ttk.LabelFrame(frame, text="外观设置", padding="10")
        appearance_frame.pack(fill=tk.X, pady=10)

        # 主题
        ttk.Label(appearance_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var, values=['light', 'dark'], state='readonly')
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # 字体大小
        ttk.Label(appearance_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.IntVar(value=self.settings.get('font_size', 10))
        font_spinbox = ttk.Spinbox(appearance_frame, from_=8, to=16, textvariable=self.font_size_var)
        font_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # 安全设置
        security_frame = ttk.LabelFrame(frame, text="安全设置", padding="10")
        security_frame.pack(fill=tk.X, pady=10)

        # 自动锁定
        ttk.Label(security_frame, text="自动锁定:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.auto_lock_var = tk.StringVar(value=self.settings.get('auto_lock', '5min'))
        auto_lock_combo = ttk.Combobox(security_frame, textvariable=self.auto_lock_var,
                                        values=['never', '1min', '5min', '15min', '30min'], state='readonly')
        auto_lock_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # 剪贴板清除
        ttk.Label(security_frame, text="剪贴板清除:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.clipboard_var = tk.StringVar(value=self.settings.get('clipboard', 'immediate'))
        clipboard_combo = ttk.Combobox(security_frame, textvariable=self.clipboard_var,
                                          values=['never', 'immediate', 'on_exit'], state='readonly')
        clipboard_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # 数据管理
        data_frame = ttk.LabelFrame(frame, text="数据管理", padding="10")
        data_frame.pack(fill=tk.X, pady=10)

        # 数据库路径
        ttk.Label(data_frame, text="数据库路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.db_path_var = tk.StringVar(value=self.settings.get('db_path', '~/.pm/pm.db'))
        db_path_entry = ttk.Entry(data_frame, textvariable=self.db_path_var, width=30)
        db_path_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        # 选择路径按钮
        ttk.Button(data_frame, text="选择...", command=self.select_db_path).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 密码强度
        security_info_frame = ttk.LabelFrame(frame, text="安全信息", padding="10")
        security_info_frame.pack(fill=tk.X, pady=10)

        ttk.Label(security_info_frame, text="密码强度检查:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.check_strength_var = tk.BooleanVar(value=self.settings.get('check_strength', True))
        ttk.Checkbutton(security_info_frame, variable=self.check_strength_var).grid(row=0, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(security_info_frame, text="重复密码检查:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.check_duplicates_var = tk.BooleanVar(value=self.settings.get('check_duplicates', True))
        ttk.Checkbutton(security_info_frame, variable=self.check_duplicates_var).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="应用", command=self.apply).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def select_db_path(self):
        """选择数据库路径"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择数据库文件",
            filetypes=[("SQLite 数据库", "*.db"), ("所有文件", "*.*")]
        )

        if file_path:
            self.db_path_var.set(file_path)

    def apply(self):
        """应用设置"""
        self.new_settings = {
            'theme': self.theme_var.get(),
            'font_size': self.font_size_var.get(),
            'auto_lock': self.auto_lock_var.get(),
            'clipboard': self.clipboard_var.get(),
            'db_path': self.db_path_var.get(),
            'check_strength': self.check_strength_var.get(),
            'check_duplicates': self.check_duplicates_var.get()
        }

        self.result = True
        self.dialog.destroy()

    def show(self) -> dict:
        """显示对话框"""
        self.dialog.wait_window()
        return self.new_settings if self.result else {}
