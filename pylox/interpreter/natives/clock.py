#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clock原生函数实现
"""

import time

class Clock:
    """
    Clock原生函数
    
    返回当前时间的秒数
    """
    
    def arity(self):
        """
        返回函数参数数量
        
        Returns:
            int: 0，表示不需要参数
        """
        return 0
    
    def call(self, interpreter, arguments):
        """
        调用函数
        
        Args:
            interpreter: Interpreter, 解释器实例
            arguments: list, 参数列表（空）
            
        Returns:
            float: 当前时间的秒数
        """
        return time.time()
    
    def __str__(self):
        """
        返回函数的字符串表示
        
        Returns:
            str: "<native fn>"
        """
        return "<native fn>"