#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
可调用对象接口和实现

包含Lox语言中可调用对象的接口和函数实现类。
"""

import time
from abc import ABC, abstractmethod
from pylox.interpreter.environment import Environment
from pylox.interpreter.return_value import Return


class LoxCallable(ABC):
    """
    可调用对象接口
    
    所有可以被调用的对象必须实现此接口。
    """
    
    @abstractmethod
    def call(self, interpreter, arguments):
        """
        调用此对象
        
        Args:
            interpreter: Interpreter, 解释器实例
            arguments: list, 参数列表
            
        Returns:
            调用结果
        """
        pass
        
    @abstractmethod
    def arity(self):
        """
        返回所需参数数量
        
        Returns:
            int: 所需参数数量
        """
        pass
        
        
class LoxFunction(LoxCallable):
    """
    Lox函数
    
    表示用户定义的函数。
    """
    
    def __init__(self, declaration, closure, is_initializer=False, is_getter=None, is_static=None):
        """
        初始化LoxFunction对象
        
        Args:
            declaration: Function, AST中的函数声明节点
            closure: Environment, 闭包环境
            is_initializer: bool, 是否是类的初始化方法
            is_getter: bool, 是否是getter方法，默认从declaration获取
            is_static: bool, 是否是静态方法，默认从declaration获取
        """
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
        
        # 如果直接提供了is_static和is_getter，则使用传入的值
        if is_static is not None:
            self.is_static = is_static
        else:
            self.is_static = declaration.is_static if hasattr(declaration, 'is_static') else False
            
        if is_getter is not None:
            self.is_getter = is_getter
        else:
            self.is_getter = declaration.is_getter if hasattr(declaration, 'is_getter') else False
        
    def call(self, interpreter, arguments):
        """
        执行函数调用
        
        创建新环境，绑定参数，执行函数体。
        
        Args:
            interpreter: Interpreter, 解释器对象
            arguments: list, 参数列表
            
        Returns:
            函数的返回值，或者None
        """
        # 创建一个新的环境
        environment = Environment(self.closure)
        
        # 检查闭包中是否有this，如果有则添加到当前环境
        try:
            instance = self.closure.get_at(0, "this")
            # 在执行环境中定义this
            environment.define("this", instance)
        except RuntimeError:
            pass  # 闭包中没有this，忽略
        
        # 只有非getter方法才需要绑定参数
        if not self.is_getter:
            # 将参数绑定到函数参数上
            for i in range(len(self.declaration.params)):
                environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            # 执行函数体
            result = interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            # 处理返回值
            if self.is_initializer:
                # 如果是初始化方法，始终返回this
                return self.closure.get_at(0, "this")
            return return_value.value
        except Exception as e:
            # 其他异常直接重新抛出
            raise
        
        # 如果是初始化方法，返回this
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        
        # 默认返回nil
        return None
        
    def bind(self, instance):
        """
        将方法绑定到实例
        
        创建新环境并将"this"绑定到实例。
        
        Args:
            instance: LoxInstance, 实例对象
            
        Returns:
            LoxFunction: 绑定了实例的新函数
        """
        environment = Environment(self.closure)
        environment.define("this", instance)
        
        # 创建新的函数，继承所有属性，但使用新环境
        # 注意：保留is_static和is_getter标志
        result = LoxFunction(self.declaration, environment, self.is_initializer, self.is_getter, self.is_static)
        return result
        
    def arity(self):
        """
        返回函数参数数量
        
        Returns:
            int: 参数数量
        """
        # getter方法不需要参数
        if self.is_getter:
            return 0
        return len(self.declaration.params)
        
    def __str__(self):
        """
        返回函数的字符串表示
        
        Returns:
            str: 函数的字符串表示
        """
        prefix = ""
        if self.is_static:
            prefix = "static "
        elif self.is_getter:
            prefix = "getter "
        return f"<{prefix}fn {self.declaration.name.lexeme}>"


class LoxLambda(LoxCallable):
    """
    Lox匿名函数实现
    
    表示用户定义的匿名函数。
    
    Attributes:
        declaration: Lambda, Lambda表达式
        closure: Environment, 闭包环境
    """
    
    def __init__(self, declaration, closure):
        """
        初始化匿名函数
        
        Args:
            declaration: Lambda, Lambda表达式
            closure: Environment, 闭包环境，用于捕获词法作用域
        """
        self.declaration = declaration
        self.closure = closure
        
    def call(self, interpreter, arguments):
        """
        调用匿名函数
        
        Args:
            interpreter: Interpreter, 解释器实例
            arguments: list, 参数列表
            
        Returns:
            函数返回值，若无返回语句则为None
        """
        # 创建一个新的环境，以闭包环境为父环境
        environment = Environment(self.closure)
        
        # 绑定参数到环境
        for i in range(len(self.declaration.params)):
            environment.define(
                self.declaration.params[i].lexeme,
                arguments[i]
            )
            
        # 执行函数体
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value
            
        return None
        
    def arity(self):
        """
        返回匿名函数所需的参数数量
        
        Returns:
            int: 参数数量
        """
        return len(self.declaration.params)
        
    def __str__(self):
        """
        返回匿名函数的字符串表示
        
        Returns:
            str: 匿名函数的字符串表示
        """
        return "<lambda fn>"


class Clock(LoxCallable):
    """
    内置函数: clock()
    
    返回当前的系统时间（以秒为单位）。
    """
    
    def call(self, interpreter, arguments):
        """
        返回当前时间（秒）
        
        Args:
            interpreter: Interpreter, 解释器实例
            arguments: list, 参数列表
            
        Returns:
            float: 当前时间（秒）
        """
        return time.time()
        
    def arity(self):
        """
        返回所需参数数量
        
        Returns:
            int: 0，不需要参数
        """
        return 0
        
    def __str__(self):
        """
        返回函数的字符串表示
        
        Returns:
            str: 函数的字符串表示
        """
        return "<native fn: clock>" 