#!/usr/bin/env python3
"""
Toast 通知系统
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, List


class ToastManager:
    """
    Toast 通知管理器

    支持多种通知类型和动画效果
    """

    def __init__(self, root: tk.Tk):
        """
        初始化 Toast 管理器

        Args:
            root: 根窗口
        """
        self.root = root
        self.toasts: List['Toast'] = []
        self.toast_duration = 3  # seconds

    def success(self, message: str, duration: Optional[int] = None):
        """
        显示成功通知

        Args:
            message: 消息内容
            duration: 显示时长（秒）
        """
        duration = duration or self.toast_duration
        self.show_toast("✅", message, "#10B981", duration)

    def error(self, message: str, duration: Optional[int] = None):
        """
        显示错误通知

        Args:
            message: 消息内容
            duration: 显示时长（秒）
        """
        duration = duration or self.toast_duration
        self.show_toast("❌", message, "#EF4444", duration)

    def info(self, message: str, duration: Optional[int] = None):
        """
        显示信息通知

        Args:
            message: 消息内容
            duration: 显示时长（秒）
        """
        duration = duration or self.toast_duration
        self.show_toast("ℹ️", message, "#3B82F6", duration)

    def warning(self, message: str, duration: Optional[int] = None):
        """
        显示警告通知

        Args:
            message: 消息内容
            duration: 显示时长（秒）
        """
        duration = duration or self.toast_duration
        self.show_toast("⚠️", message, "#F59E0B", duration)

    def show_toast(self, icon: str, message: str, color: str, duration: int):
        """
        显示 Toast

        Args:
            icon: 图标
            message: 消息
            color: 颜色
            duration: 显示时长
        """
        toast = Toast(self.root, icon, message, color, duration)
        self.toasts.append(toast)

        # Position toast
        toast.position()

        # Animate in
        toast.animate_in()

        # Auto dismiss
        self.root.after(duration * 1000, lambda: toast.dismiss())


class Toast(tk.Toplevel):
    """
    Toast 通知组件
    """

    def __init__(self, root: tk.Tk, icon: str, message: str, color: str, duration: int):
        """
        初始化 Toast

        Args:
            root: 根窗口
            icon: 图标
            message: 消息
            color: 颜色
            duration: 显示时长（秒）
        """
        super().__init__(root)

        self.icon = icon
        self.message = message
        self.color = color
        self.duration = duration

        # 设置窗口属性
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0)  # 初始隐藏
        self.geometry('400x60+100+100')  # 初始位置

        # 创建内容
        self.create_content()

        # 居中显示
        self.update_idletasks()
        self.after(100, self.animate_in)

    def create_content(self):
        """创建内容"""
        # 背景卡片
        card = tk.Frame(self, bg=self.color, padx=16, pady=12)
        card.pack(fill=tk.BOTH, expand=True)

        # 图标 + 消息
        content = tk.Frame(card, bg=self.color)
        content.pack(side=tk.LEFT)

        icon_label = tk.Label(content, text=self.icon, font=('Arial', 20), bg=self.color, fg='white')
        icon_label.pack(side=tk.LEFT, padx=(0, 12))

        message_label = tk.Label(content, text=self.message, font=('Arial', 12), bg=self.color, fg='white')
        message_label.pack(side=tk.LEFT)

    def position(self):
        """定位 Toast（右下角）"""
        self.update_idletasks()

        # 计算位置
        root_x = self.root.winfo_rootx() + self.root.winfo_width()
        root_y = self.root.winfo_rooty() + self.root.winfo_height()

        self_x = root_x - 420
        self_y = root_y - 80

        self.geometry(f'400x60+{self_x}+{self_y}')

    def animate_in(self):
        """动画显示"""
        for i in range(10):
            alpha = i / 10
            self.attributes('-alpha', alpha)
            self.update()
            self.root.after(20)

    def dismiss(self):
        """隐藏并销毁"""
        for i in range(10):
            alpha = 1 - (i / 10)
            self.attributes('-alpha', alpha)
            self.update()
            self.root.after(20)

        self.after(200, self.destroy)
