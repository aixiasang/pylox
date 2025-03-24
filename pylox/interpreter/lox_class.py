#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lox类和实例的实现

提供Lox语言中类和实例对象的实现。
"""

from pylox.interpreter.lox_callable import LoxCallable
from pylox.interpreter.runtime_error import RuntimeError


class LoxClass(LoxCallable):
    """
    Lox类
    
    表示一个Lox类，可以被实例化并包含方法。
    """
    
    def __init__(self, name, superclass, methods):
        """
        初始化Lox类
        
        Args:
            name: str, 类名
            superclass: LoxClass, 父类，可以为None
            methods: dict, 方法字典，键为方法名，值为LoxFunction对象
        """
        self.name = name
        self.superclass = superclass
        self.methods = {}
        self.static_methods = {}
        
        # 分类方法
        for method_name, method in methods.items():
            if method.is_static:
                self.static_methods[method_name] = method
            else:
                self.methods[method_name] = method
        
    def call(self, interpreter, arguments):
        """
        调用类构造函数创建实例
        
        Args:
            interpreter: Interpreter, 解释器实例
            arguments: list, 参数列表
            
        Returns:
            LoxInstance: 新创建的实例
        """
        instance = LoxInstance(self)
        
        # 查找并调用初始化方法
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
            
        return instance
        
    def find_method(self, name):
        """
        查找实例方法
        
        首先在当前类中查找，如果找不到则在父类中查找。
        
        Args:
            name: str, 方法名
            
        Returns:
            LoxFunction: 方法对象，如果不存在则返回None
        """
        if name in self.methods:
            return self.methods[name]
            
        # 如果有父类，在父类中查找
        if self.superclass is not None:
            return self.superclass.find_method(name)
            
        return None
    
    def find_static_method(self, name):
        """
        查找静态方法
        
        首先在当前类中查找，如果找不到则在父类中查找。
        
        Args:
            name: str, 静态方法名
            
        Returns:
            LoxFunction: 静态方法对象，如果不存在则返回None
        """
        if name in self.static_methods:
            return self.static_methods[name]
            
        # 如果有父类，在父类中查找
        if self.superclass is not None:
            return self.superclass.find_static_method(name)
            
        return None
        
    def arity(self):
        """
        返回构造函数需要的参数数量
        
        如果有初始化方法，返回其参数数量，否则返回0
        
        Returns:
            int: 参数数量
        """
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()
        
    def __str__(self):
        """
        返回类的字符串表示
        
        Returns:
            str: 类的字符串表示
        """
        return f"<class {self.name}>"


class LoxInstance:
    """
    Lox实例
    
    表示一个Lox类的实例，包含字段和方法。
    """
    
    def __init__(self, klass):
        """
        初始化Lox实例
        
        Args:
            klass: LoxClass, 类对象
        """
        self.klass = klass
        self.fields = {}  # 实例字段
        
    def get(self, name, interpreter):
        """
        获取实例字段或方法
        
        首先检查实例字段，如果找不到再查找类方法
        
        Args:
            name: Token, 字段或方法名标记
            interpreter: Interpreter, 解释器实例
            
        Returns:
            字段值或绑定到此实例的方法
            
        Raises:
            RuntimeError: 如果字段或方法不存在
        """
        # 首先检查实例的字段
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        # 然后查找类中的方法
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            # 将方法绑定到当前实例
            method = method.bind(self)
            
            # 如果是getter方法，直接执行它
            if method.is_getter:
                try:
                    # 直接调用getter方法，不传递参数
                    return method.call(interpreter, [])
                except Exception as e:
                    # 处理Return异常，这是执行块时抛出的正常异常
                    from pylox.interpreter.interpreter import Return
                    if isinstance(e, Return):
                        return e.value
                    
                    # 如果是其他异常，重新抛出
                    raise
            
            return method
        
        # 如果找不到，抛出运行时错误
        raise RuntimeError(name, f"未定义的属性 '{name.lexeme}'。")
        
    def set(self, name, value):
        """
        设置实例字段
        
        Args:
            name: Token, 字段名标记
            value: 任意值，字段值
            
        Returns:
            None
        """
        self.fields[name.lexeme] = value
        
    def __str__(self):
        """
        返回实例的字符串表示
        
        Returns:
            str: 实例的字符串表示
        """
        return f"<{self.klass.name} instance>"