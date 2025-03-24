#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境类定义

实现变量的作用域和生命周期管理。
"""

from pylox.interpreter.runtime_error import RuntimeError


class Environment:
    """
    环境类
    
    表示变量的作用域，存储变量名和值的映射关系。
    支持嵌套作用域。
    """
    
    def __init__(self, enclosing=None):
        """
        初始化环境
        
        Args:
            enclosing: Environment, 外层环境，默认为None
        """
        self.values = {}  # 变量名到值的映射
        self.enclosing = enclosing  # 外层环境
        
    def define(self, name, value):
        """
        定义变量
        
        Args:
            name: str, 变量名
            value: 任意类型，变量值
        """
        self.values[name] = value
        
    def get(self, name):
        """
        获取变量的值
        
        Args:
            name: Token, 变量名标记
            
        Returns:
            变量的值
            
        Raises:
            RuntimeError: 如果变量未定义或未初始化
        """
        if name.lexeme in self.values:
            value = self.values[name.lexeme]
            if value is None:
                from pylox.interpreter.runtime_error import RuntimeError
                raise RuntimeError(name, f"未初始化的变量 '{name.lexeme}'。")
            return value
            
        if self.enclosing:
            return self.enclosing.get(name)
            
        from pylox.interpreter.runtime_error import RuntimeError
        raise RuntimeError(name, f"未定义的变量 '{name.lexeme}'。")
        
    def assign(self, name, value):
        """
        给变量赋值
        
        Args:
            name: Token, 变量名标记
            value: 任意类型，变量值
            
        Returns:
            None
            
        Raises:
            RuntimeError: 如果变量未定义
        """
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
            
        if self.enclosing:
            self.enclosing.assign(name, value)
            return
            
        from pylox.interpreter.runtime_error import RuntimeError
        raise RuntimeError(name, f"未定义的变量 '{name.lexeme}'。")
        
    def ancestor(self, distance):
        """
        获取指定深度的环境
        
        Args:
            distance: int, 环境深度
            
        Returns:
            Environment: 指定深度的环境
        """
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment
        
    def get_at(self, distance, name):
        """
        从特定深度的环境中获取变量值
        
        Args:
            distance: int, 环境深度
            name: str, 变量名
            
        Returns:
            变量的值
            
        Raises:
            RuntimeError: 如果变量未初始化
        """
        value = self.ancestor(distance).values.get(name)
        if value is None and name != "super" and name != "this":  # super和this总是合法的，可以为None
            from pylox.interpreter.runtime_error import RuntimeError
            raise RuntimeError(None, f"未初始化的变量 '{name}'。")
        return value
        
    def assign_at(self, distance, name, value):
        """
        在指定深度的环境中给变量赋值
        
        Args:
            distance: int, 环境深度
            name: Token, 变量名标记
            value: 任意类型，变量值
        """
        self.ancestor(distance).values[name.lexeme] = value
        
    def get_outer_variable(self, name_str):
        """
        获取外部作用域中的变量（跳过当前作用域）
        
        用于初始化时引用外部同名变量
        
        Args:
            name_str: str, 变量名
            
        Returns:
            变量的值，如果不存在则返回None
        """
        if self.enclosing:
            return self.enclosing.get_by_name(name_str)
        return None
        
    def get_by_name(self, name_str):
        """
        通过变量名获取变量的值
        
        Args:
            name_str: str, 变量名
            
        Returns:
            变量的值，如果不存在则返回None
        """
        if name_str in self.values:
            return self.values[name_str]
            
        if self.enclosing:
            return self.enclosing.get_by_name(name_str)
            
        return None 