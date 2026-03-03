#!/usr/bin/env python3
"""
欢迎页面
"""

import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from typing import Callable


class WelcomePage(tk.Frame):
    """
    欢迎页面

    首次启动时显示，引导用户初始化数据库
    """

    def __init__(self, parent: tk.Tk, on_init: Callable[[], None], on_import: Callable[[str], None]):
        """
        初始化欢迎页面

        Args:
            parent: 父窗口
            on_init: 初始化回调
            on_import: 导入回调
        """
        super().__init__(parent)
        self.on_init = on_init
        self.on_import = on_import

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.create_widgets()

    def create_widgets(self):
        """创建所有组件"""
        # 内容容器
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)

        # 标题
        title_frame = ttk.Frame(container)
        title_frame.pack(fill=tk.X, pady=30)

        # 图标
        icon_label = tk.Label(title_frame, text="🔐", font=('Arial', 80))
        icon_label.pack(pady=20)

        # 主标题
        title_label = tk.Label(title_frame, text="欢迎使用密码管理器", font=('Arial', 28, 'bold'))
        title_label.pack(pady=10)

        # 副标题
        subtitle_label = tk.Label(title_frame, text="安全、简单、强大", font=('Arial', 14), fg='#666')
        subtitle_label.pack(pady=5)

        # 操作按钮
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=50)

        # 初始化新数据库
        init_btn = ttk.Button(
            button_frame,
            text="创建新的主密码",
            command=self.on_init,
            width=30
        )
        init_btn.pack(pady=10)

        # 恢复现有数据库
        import_frame = ttk.Frame(button_frame)
        import_frame.pack(fill=tk.X, pady=20)

        ttk.Label(import_frame, text="已有数据库？").pack(pady=10)

        import_btn = ttk.Button(
            import_frame,
            text="恢复现有数据库",
            command=self.select_database,
            width=30
        )
        import_btn.pack()

        # 功能介绍
        features_frame = ttk.LabelFrame(container, text="核心功能", padding=20)
        features_frame.pack(fill=tk.X, pady=30)

        features = [
            ("🔐 强加密", "AES-256-GCM 军事级加密"),
            ("🎲 密码生成", "自定义长度和字符类型"),
            ("🔍 快速搜索", "实时搜索和分类"),
            ("📁 数据管理", "安全的导出和导入"),
            ("🎨 现代界面", "直观易用的用户界面")
        ]

        for icon, description in features:
            feature_frame = ttk.Frame(features_frame)
            feature_frame.pack(fill=tk.X, pady=8)

            icon_label = tk.Label(feature_frame, text=icon, font=('Arial', 16))
            icon_label.pack(side=tk.LEFT, padx=10)

            desc_label = tk.Label(feature_frame, text=description, font=('Arial', 12))
            desc_label.pack(side=tk.LEFT)

    def select_database(self):
        """选择现有数据库"""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="选择数据库文件",
            filetypes=[("SQLite 数据库", "*.db"), ("所有文件", "*.*")]
        )

        if file_path:
            self.on_import(file_path)


def show_welcome_dialog(parent: tk.Tk, on_init: Callable[[], None], on_import: Callable[[str], None]) -> None:
    """
    显示欢迎对话框

    Args:
        parent: 父窗口
        on_init: 初始化回调
        on_import: 导入回调
    """
    dialog = tk.Toplevel(parent)
    dialog.title("密码管理器")
    dialog.geometry("600x700")
    dialog.transient(parent)
    dialog.grab_set()

    welcome_page = WelcomePage(dialog, on_init, on_import)
    welcome_page.pack(fill=tk.BOTH, expand=True)

    dialog.wait_window()
