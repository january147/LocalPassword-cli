#!/usr/bin/env python3
"""
主题管理器
"""

import tkinter as tk
from typing import Dict
import json


class ThemeManager:
    """
    主题管理器

    支持亮色和暗色主题
    """

    def __init__(self):
        """初始化主题管理器"""
        self.current_theme = 'light'

        # 定义主题
        self.themes: Dict[str, Dict[str, str]] = {
            'light': {
                'bg': '#F9FAFB',
                'fg': '#1F2937',
                'card_bg': '#FFFFFF',
                'card_fg': '#1F2937',
                'input_bg': '#FFFFFF',
                'input_fg': '#1F2937',
                'border': '#E5E7EB',
                'button_bg': '#3B82F6',
                'button_fg': '#FFFFFF',
                'button_hover_bg': '#2563EB',
                'accent': '#3B82F6',
                'success': '#10B981',
                'warning': '#F59E0B',
                'error': '#EF4444'
            },
            'dark': {
                'bg': '#111827',
                'fg': '#F9FAFB',
                'card_bg': '#1F2937',
                'card_fg': '#F9FAFB',
                'input_bg': '#374151',
                'input_fg': '#F9FAFB',
                'border': '#374151',
                'button_bg': '#2563EB',
                'button_fg': '#FFFFFF',
                'button_hover_bg': '#1D4ED8',
                'accent': '#60A5FA',
                'success': '#10B981',
                'warning': '#F59E0B',
                'error': '#EF4444'
            }
        }

    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """
        获取主题配置

        Args:
            theme_name: 主题名称（默认当前主题）

        Returns:
            主题配置字典
        """
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes['light'])

    def set_theme(self, theme_name: str):
        """
        设置当前主题

        Args:
            theme_name: 主题名称
        """
        if theme_name in self.themes:
            self.current_theme = theme_name

    def apply_theme(self, root: tk.Tk, style: ttk.Style, theme_name: Optional[str] = None):
        """
        应用主题到窗口

        Args:
            root: 根窗口
            style: Ttk 样式对象
            theme_name: 主题名称
        """
        theme = self.get_theme(theme_name)

        # 应用基础样式
        style.configure('TFrame', background=theme['bg'])
        style.configure('TLabelframe', background=theme['bg'], foreground=theme['fg'])
        style.configure('TButton',
                       background=theme['button_bg'],
                       foreground=theme['button_fg'])
        style.map('TButton',
                  background=[('active', theme['button_hover_bg'])])
        style.configure('TEntry',
                       fieldbackground=theme['input_bg'],
                       foreground=theme['input_fg'],
                       insertbackground=theme['input_bg'])
        style.configure('Treeview',
                       background=theme['bg'],
                       foreground=theme['fg'],
                       fieldbackground=theme['card_bg'])
        style.configure('Treeview.Heading',
                       background=theme['card_bg'],
                       foreground=theme['fg'])
        style.configure('Treeview.row',
                       background=theme['bg'],
                       foreground=theme['fg'])

        # 配置窗口
        root.configure(bg=theme['bg'])

    def toggle_theme(self, root: tk.Tk, style: ttk.Style) -> str:
        """
        切换主题

        Args:
            root: 根窗口
            style: Ttk 样式对象

        Returns:
            新主题名称
        """
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.set_theme(new_theme)
        self.apply_theme(root, style, new_theme)
        return new_theme

    def get_available_themes(self) -> Dict[str, str]:
        """
        获取可用主题列表

        Returns:
            主题名称到显示名称的映射
        """
        return {
            'light': '亮色主题',
            'dark': '暗色主题'
        }
