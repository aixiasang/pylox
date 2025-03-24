#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
表达式类定义，用于构建抽象语法树

这个模块定义了Lox语言中各种表达式的类层次结构。
每种表达式类型都是Expr的子类，并支持访问者模式。
"""

from abc import ABC, abstractmethod
from pylox.scanner.token import Token


class Expr(ABC):
    """
    表达式抽象基类
    
    所有具体表达式类型都继承自这个类，并必须实现accept方法
    """
    
    @abstractmethod
    def accept(self, visitor):
        """
        接受一个访问者对象并调用相应的visit方法
        
        Args:
            visitor: 访问者对象，实现了Visitor接口
            
        Returns:
            访问者处理表达式的结果
        """
        pass


class Binary(Expr):
    """
    二元表达式
    
    表示形如 "left operator right" 的表达式。
    例如：1 + 2, a > b 等。
    """
    
    def __init__(self, left, operator, right):
        """
        初始化二元表达式
        
        Args:
            left: Expr, 左操作数
            operator: Token, 运算符
            right: Expr, 右操作数
        """
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理表达式的结果
        """
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    """
    分组表达式
    
    表示被括号括起来的表达式。
    例如：(1 + 2)
    """
    
    def __init__(self, expression):
        """
        初始化分组表达式
        
        Args:
            expression: Expr, 被括号包围的表达式
        """
        self.expression = expression
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理表达式的结果
        """
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    """
    字面量表达式
    
    表示常量值，如数字、字符串、布尔值等。
    例如：123, "hello", true
    """
    
    def __init__(self, value):
        """
        初始化字面量表达式
        
        Args:
            value: 任意类型，字面量的值
        """
        self.value = value
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理表达式的结果
        """
        return visitor.visit_literal_expr(self)


class Unary(Expr):
    """
    一元表达式
    
    表示形如 "operator right" 的表达式。
    例如：!true, -123
    """
    
    def __init__(self, operator, right):
        """
        初始化一元表达式
        
        Args:
            operator: Token, 运算符
            right: Expr, 操作数
        """
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理表达式的结果
        """
        return visitor.visit_unary_expr(self)


class Variable(Expr):
    """
    变量表达式
    
    表示变量引用。
    例如：x, counter
    """
    
    def __init__(self, name, is_outer_ref=False):
        """
        初始化变量表达式
        
        Args:
            name: Token, 变量名标记
            is_outer_ref: bool, 是否引用外部作用域的同名变量
        """
        self.name = name
        self._is_outer_ref = is_outer_ref
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理表达式的结果
        """
        return visitor.visit_variable_expr(self)


class Assign(Expr):
    """
    赋值表达式
    
    表示变量赋值。
    例如：x = 42
    """
    
    def __init__(self, name, value):
        """
        初始化赋值表达式
        
        Args:
            name: Token, 变量名标记
            value: Expr, 赋值表达式
        """
        self.name = name
        self.value = value
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理表达式的结果
        """
        return visitor.visit_assign_expr(self)


class Logical(Expr):
    """
    逻辑表达式
    
    表示逻辑操作的表达式，如and和or。
    """
    
    def __init__(self, left, operator, right):
        """
        初始化逻辑表达式
        
        Args:
            left: Expr, 左操作数
            operator: Token, 操作符标记
            right: Expr, 右操作数
        """
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了visit_logical_expr方法的访问者
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_logical_expr(self)


class Call(Expr):
    """
    函数调用表达式
    
    表示函数调用，包含被调用对象、括号位置和参数列表。
    """
    
    def __init__(self, callee, paren, arguments):
        """
        初始化函数调用表达式
        
        Args:
            callee: Expr, 被调用对象
            paren: Token, 左括号位置
            arguments: list, 参数列表
        """
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: Visitor, 访问者对象
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_call_expr(self)


class Lambda(Expr):
    """
    匿名函数（Lambda）表达式
    
    表示形如 fun (arg1, arg2, ...) { body } 的匿名函数定义。
    
    Attributes:
        params: list[Token], 参数列表
        body: list[Stmt], 函数体
    """
    
    def __init__(self, params, body):
        """
        初始化Lambda表达式
        
        Args:
            params: list[Token], 参数列表
            body: list[Stmt], 函数体
        """
        self.params = params
        self.body = body
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了相应visit方法的访问者
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_lambda_expr(self)


class Get(Expr):
    """
    属性访问表达式
    
    表示对象属性访问，如obj.prop
    """
    
    def __init__(self, object, name):
        """
        初始化属性访问表达式
        
        Args:
            object: Expr, 对象表达式
            name: Token, 属性名
        """
        self.object = object
        self.name = name
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: Visitor, 访问者对象
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_get_expr(self)


class Set(Expr):
    """
    属性设置表达式
    
    表示对象属性设置，如obj.prop = value
    """
    
    def __init__(self, object, name, value):
        """
        初始化属性设置表达式
        
        Args:
            object: Expr, 对象表达式
            name: Token, 属性名
            value: Expr, 值表达式
        """
        self.object = object
        self.name = name
        self.value = value
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: Visitor, 访问者对象
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_set_expr(self)


class This(Expr):
    """
    This表达式节点
    
    表示this关键字。
    """
    
    def __init__(self, keyword):
        """
        初始化This表达式节点
        
        Args:
            keyword: Token, this关键字的标记
        """
        self.keyword = keyword
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了visit_this_expr方法的访问者
            
        Returns:
            visitor.visit_this_expr的返回值
        """
        return visitor.visit_this_expr(self)


class Super(Expr):
    """
    Super表达式节点
    
    表示super关键字访问父类方法。
    """
    
    def __init__(self, keyword, method):
        """
        初始化Super表达式节点
        
        Args:
            keyword: Token, super关键字的标记
            method: Token, 要访问的方法名
        """
        self.keyword = keyword
        self.method = method
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了visit_super_expr方法的访问者
            
        Returns:
            visitor.visit_super_expr的返回值
        """
        return visitor.visit_super_expr(self)