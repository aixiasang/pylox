#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
返回值异常

用于从函数返回值。当执行return语句时，引发此异常并携带返回值，
由最内层的函数调用捕获。
"""


class Return(Exception):
    """
    返回值异常
    
    当执行return语句时，引发此异常并携带返回值，用于从任意嵌套深度返回值。
    
    Attributes:
        value: 返回值
    """
    
    def __init__(self, value):
        """
        初始化返回值异常
        
        Args:
            value: 返回值
        """
        super().__init__(self)
        self.value = value 