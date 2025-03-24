#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化的解释器实现

使用数组索引代替映射查找，提高变量访问性能。
"""

from pylox.syntax_tree.visitor import Visitor
from pylox.scanner.token_type import TokenType
from pylox.interpreter.runtime_error import RuntimeError
from pylox.interpreter.optimized_environment import OptimizedEnvironment
from pylox.interpreter.lox_callable import LoxCallable, LoxFunction, Clock, LoxLambda
from pylox.interpreter.return_value import Return


class BreakException(Exception):
    """
    Break语句异常
    
    当执行break语句时抛出，用于跳出循环。
    """
    pass


class OptimizedInterpreter(Visitor):
    """
    优化的Lox解释器
    
    使用数组索引代替映射查找，提高变量访问性能。
    """
    
    def __init__(self):
        """初始化解释器"""
        self.environment = OptimizedEnvironment()
        self.globals = self.environment  # 全局环境引用
        
        # 变量解析结果存储
        self.locals = {}  # 表达式 -> (深度, 索引)
        
        # 定义内置函数
        self.globals.define_global("clock", Clock())
        
    def interpret(self, statements):
        """
        解释执行语句列表
        
        Args:
            statements: list[Stmt], 语句列表
            
        Returns:
            解释执行的结果，通常为None
        """
        try:
            result = None
            for statement in statements:
                result = self.execute(statement)
            return result
        except RuntimeError as error:
            from pylox.lox import Lox
            Lox.runtime_error(error)
            return None
    
    def resolve_optimized(self, expr, depth, index):
        """
        存储优化的变量引用解析结果
        
        Args:
            expr: Expr, 表达式对象（变量引用）
            depth: int, 变量声明的作用域深度
            index: int, 变量在数组中的索引
        """
        self.locals[expr] = (depth, index)
    
    def execute(self, stmt):
        """
        执行单个语句
        
        Args:
            stmt: Stmt, 语句对象
            
        Returns:
            语句执行结果，通常为None
        """
        return stmt.accept(self)
    
    def execute_block(self, statements, environment):
        """
        在指定环境中执行语句块
        
        Args:
            statements: list[Stmt], 语句列表
            environment: OptimizedEnvironment, 执行环境
            
        Returns:
            语句块执行结果，通常为None
        """
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
                
            return None
        finally:
            self.environment = previous
    
    def visit_variable_expr(self, expr):
        """
        访问变量表达式
        
        Args:
            expr: Variable, 变量表达式
            
        Returns:
            变量的值
        """
        return self.look_up_variable(expr.name, expr)
    
    def look_up_variable(self, name, expr):
        """
        查找变量的值
        
        使用优化的索引查找变量。
        
        Args:
            name: Token, 变量名标记
            expr: Expr, 变量引用表达式
            
        Returns:
            变量的值
        """
        resolution = self.locals.get(expr)
        if resolution is not None:
            depth, index = resolution
            return self.environment.ancestor(depth).get_at_index(index)
        else:
            return self.globals.get_global(name)
    
    def visit_assign_expr(self, expr):
        """
        访问赋值表达式
        
        Args:
            expr: Assign, 赋值表达式
            
        Returns:
            赋值的值
        """
        value = self.evaluate(expr.value)
        
        resolution = self.locals.get(expr)
        if resolution is not None:
            depth, index = resolution
            self.environment.ancestor(depth).assign_at_index(index, value)
        else:
            self.globals.assign_global(expr.name, value)
            
        return value
    
    # 其他方法与普通解释器相同
    # ...
    
    def _stringify(self, value):
        """
        将值转换为字符串表示形式
        
        Args:
            value: 要转换的值
            
        Returns:
            str: 值的字符串表示
        """
        if value is None:
            return "nil"
            
        if isinstance(value, bool):
            return str(value).lower()
            
        if isinstance(value, (int, float)):
            text = str(value)
            if text.endswith('.0'):
                text = text[:-2]
            return text
            
        # 如果是字符串，处理常见的转义字符
        if isinstance(value, str):
            return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r")
            
        return str(value)