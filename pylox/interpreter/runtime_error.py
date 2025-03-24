#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
运行时错误类

定义Lox解释器的运行时错误类，用于表示执行过程中的错误。
"""

from pylox.scanner.token import Token


class RuntimeError(Exception):
    """
    Lox运行时错误
    
    表示Lox程序执行过程中发生的错误，包含错误发生的标记位置信息。
    """
    
    def __init__(self, token, message):
        """
        初始化运行时错误
        
        Args:
            token: Token, 发生错误的标记
            message: str, 错误消息
        """
        super().__init__(message)
        self.token = token
