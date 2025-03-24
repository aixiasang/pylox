#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化的环境类

使用数组而非哈希表存储局部变量，提高访问效率。
"""

from pylox.interpreter.runtime_error import RuntimeError


class OptimizedEnvironment:
    """
    优化的环境类
    
    使用数组存储变量，通过索引快速访问，提高性能。
    """
    
    def __init__(self, enclosing=None):
        """
        初始化环境
        
        Args:
            enclosing: OptimizedEnvironment, 外层环境，默认为None
        """
        self.values = []  # 使用数组存储变量值
        self.globals = {}  # 仍使用字典存储全局变量
        self.enclosing = enclosing
        
    def define_at_index(self, index, value):
        """
        在指定索引定义变量
        
        Args:
            index: int, 变量索引
            value: 变量值
        """
        # 确保数组大小足够
        while len(self.values) <= index:
            self.values.append(None)
        
        self.values[index] = value
        
    def define_global(self, name, value):
        """
        定义全局变量
        
        Args:
            name: str, 变量名
            value: 变量值
        """
        self.globals[name] = value
        
    def get_at_index(self, index):
        """
        通过索引获取变量值
        
        Args:
            index: int, 变量索引
            
        Returns:
            变量的值
            
        Raises:
            IndexError: 如果索引无效
        """
        if 0 <= index < len(self.values):
            return self.values[index]
        
        raise IndexError(f"无效的变量索引: {index}")
    
    def get_global(self, name):
        """
        获取全局变量值
        
        Args:
            name: Token, 变量名标记
            
        Returns:
            变量的值
            
        Raises:
            RuntimeError: 如果变量未定义
        """
        if name.lexeme in self.globals:
            return self.globals[name.lexeme]
            
        raise RuntimeError(name, f"未定义的变量'{name.lexeme}'。")
    
    def assign_at_index(self, index, value):
        """
        通过索引修改变量值
        
        Args:
            index: int, 变量索引
            value: 新的变量值
            
        Raises:
            IndexError: 如果索引无效
        """
        if 0 <= index < len(self.values):
            self.values[index] = value
            return
        
        raise IndexError(f"无效的变量索引: {index}")
    
    def assign_global(self, name, value):
        """
        修改全局变量值
        
        Args:
            name: Token, 变量名标记
            value: 新的变量值
            
        Returns:
            None
            
        Raises:
            RuntimeError: 如果变量未定义
        """
        if name.lexeme in self.globals:
            self.globals[name.lexeme] = value
            return
            
        raise RuntimeError(name, f"未定义的变量'{name.lexeme}'。")
    
    def ancestor(self, distance):
        """
        获取指定深度的环境
        
        Args:
            distance: int, 环境深度
            
        Returns:
            OptimizedEnvironment: 指定深度的环境
        """
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        
        return environment