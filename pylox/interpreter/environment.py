#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
环境类实现
用于管理变量的存储与访问
"""

from pylox.interpreter.runtime_error import RuntimeError


class Environment:
    """
    环境类，管理变量的存储与访问
    
    在Lox中，环境表示一个变量的作用域，它可以嵌套形成作用域链
    支持变量的定义、获取与赋值操作
    """
    
    def __init__(self, enclosing=None):
        """
        初始化环境
        
        Args:
            enclosing: Environment, 外部环境，默认为None表示全局环境
        """
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name, value):
        """
        定义一个变量
        
        Args:
            name: str, 变量名
            value: Any, 变量值，可以为None表示未初始化
        """
        self.values[name] = value
    
    def ancestor(self, distance):
        """
        获取指定距离的祖先环境
        
        Args:
            distance: int, 向上查找的层数
            
        Returns:
            Environment: 找到的环境
        """
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        
        return environment
    
    def get_at(self, distance, name):
        """
        在指定距离的环境中获取变量值
        
        Args:
            distance: int, 向上查找的层数
            name: str, 变量名
            
        Returns:
            Any: 变量值
        """
        # 获取指定距离的环境
        return self.ancestor(distance).values.get(name)
    
    def assign_at(self, distance, name, value):
        """
        在指定距离的环境中赋值变量
        
        Args:
            distance: int, 向上查找的层数
            name: str, 变量名
            value: Any, 变量值
        """
        # 获取指定距离的环境并赋值
        self.ancestor(distance).values[name.lexeme] = value
    
    def get(self, name):
        """
        获取变量值
        
        Args:
            name: Token, 变量名标记
            
        Returns:
            Any: 变量值
            
        Raises:
            RuntimeError: 变量未定义或未初始化
        """
        if name.lexeme in self.values:
            value = self.values[name.lexeme]
            # 这里有特殊处理：如果值为None，可能表示未初始化的变量
            if value is None:
                raise RuntimeError(name, f"未初始化的变量 '{name.lexeme}'。")
            return value
        
        # 如果在当前环境中找不到，则查找外层环境
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        # 变量未定义
        raise RuntimeError(name, f"未定义的变量 '{name.lexeme}'。")
    
    def assign(self, name, value):
        """
        变量赋值
        
        Args:
            name: Token, 变量名标记
            value: Any, 变量值
            
        Raises:
            RuntimeError: 变量未定义
        """
        if name.lexeme in self.values:
            # 在当前环境中找到变量，进行赋值
            self.values[name.lexeme] = value
            return
        
        # 如果当前环境中没有该变量，则在外层环境中查找
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        # 变量未定义
        raise RuntimeError(name, f"未定义的变量 '{name.lexeme}'。")

    def get_from_enclosing(self, name_str):
        """
        从外部环境中获取变量值，用于块内变量初始化
        
        Args:
            name_str: str, 变量名
            
        Returns:
            Any: 变量值
        """
        if self.enclosing:
            if name_str in self.enclosing.values:
                return self.enclosing.values[name_str]
            return self.enclosing.get_from_enclosing(name_str)
        return None