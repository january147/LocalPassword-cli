#!/usr/bin/env python3
"""
密码强度分析器
"""

import re
from typing import Dict, Tuple


class PasswordStrengthAnalyzer:
    """
    密码强度分析器
    """

    def __init__(self):
        """初始化分析器"""
        self.length_weight = 0.3
        self.complexity_weight = 0.3
        self.variety_weight = 0.4

    def analyze(self, password: str) -> Dict[str, any]:
        """
        分析密码强度

        Args:
            password: 密码

        Returns:
            分析结果字典
        """
        if not password:
            return {
                'strength': 'none',
                'score': 0,
                'level': '未设置',
                'color': '#9CA3AF',
                'bar_width': 0
            }

        # 计算各项得分
        length_score = self._calculate_length_score(password)
        complexity_score = self._calculate_complexity_score(password)
        variety_score = self._calculate_variety_score(password)

        # 计算总分
        total_score = (
            length_score * self.length_weight +
            complexity_score * self.complexity_weight +
            variety_score * self.variety_weight
        )

        # 确定等级
        strength, level, color, bar_width = self._get_strength_info(total_score)

        # 详细信息
        details = {
            'length': len(password),
            'length_score': length_score,
            'complexity_score': complexity_score,
            'variety_score': variety_score,
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_numbers': bool(re.search(r'[0-9]', password)),
            'has_symbols': bool(re.search(r'[^A-Za-z0-9]', password))
        }

        return {
            'strength': strength,
            'score': round(total_score, 2),
            'level': level,
            'color': color,
            'bar_width': bar_width,
            'details': details
        }

    def _calculate_length_score(self, password: str) -> float:
        """计算长度得分"""
        length = len(password)

        if length < 8:
            return 0.3
        elif length < 12:
            return 0.6
        elif length < 16:
            return 0.9
        else:
            return 1.0

    def _calculate_complexity_score(self, password: str) -> float:
        """计算复杂度得分"""
        has_uppercase = bool(re.search(r'[A-Z]', password))
        has_lowercase = bool(re.search(r'[a-z]', password))
        has_numbers = bool(re.search(r'[0-9]', password))
        has_symbols = bool(re.search(r'[^A-Za-z0-9]', password))

        score = 0
        if has_uppercase:
            score += 0.25
        if has_lowercase:
            score += 0.25
        if has_numbers:
            score += 0.25
        if has_symbols:
            score += 0.25

        return score

    def _calculate_variety_score(self, password: str) -> float:
        """计算字符类型得分"""
        char_types = 0

        if re.search(r'[A-Z]', password):
            char_types += 1
        if re.search(r'[a-z]', password):
            char_types += 1
        if re.search(r'[0-9]', password):
            char_types += 1
        if re.search(r'[^A-Za-z0-9]', password):
            char_types += 1

        if char_types == 1:
            return 0.3
        elif char_types == 2:
            return 0.6
        elif char_types == 3:
            return 0.9
        else:
            return 1.0

    def _get_strength_info(self, score: float) -> Tuple[str, str, str, int]:
        """
        根据得分获取强度信息

        Args:
            score: 得分

        Returns:
            (strength, level, color, bar_width)
        """
        if score < 0.3:
            return ('very_weak', '很弱', '#EF4444', 20)
        elif score < 0.5:
            return ('weak', '弱', '#F59E0B', 40)
        elif score < 0.7:
            return ('medium', '中等', '#F59E0B', 60)
        elif score < 0.9:
            return ('strong', '强', '#10B981', 80)
        else:
            return ('very_strong', '很强', '#10B981', 100)

    def get_recommendations(self, password: str) -> list:
        """
        获取密码改进建议

        Args:
            password: 密码

        Returns:
            建议列表
        """
        recommendations = []

        # 长度检查
        if len(password) < 12:
            recommendations.append('建议增加密码长度到至少 12 位')

        # 复杂度检查
        if not re.search(r'[A-Z]', password):
            recommendations.append('建议添加大写字母')
        if not re.search(r'[a-z]', password):
            recommendations.append('建议添加小写字母')
        if not re.search(r'[0-9]', password):
            recommendations.append('建议添加数字')
        if not re.search(r'[^A-Za-z0-9]', password):
            recommendations.append('建议添加特殊字符')

        # 常见模式检查
        if re.search(r'(.)\1{2,}', password):
            recommendations.append('避免连续重复相同的字符')
        if re.search(r'(abc|123|qwe)', password.lower()):
            recommendations.append('避免使用常见的连续字符')

        return recommendations
