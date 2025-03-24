#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语句类定义，用于构建抽象语法树

定义了Lox语言中各种语句的类层次结构。
每种语句类型都是Stmt的子类，并支持访问者模式。
"""

from abc import ABC, abstractmethod


class Stmt(ABC):
    """
    语句抽象基类
    
    所有具体语句类型都继承自这个类，并必须实现accept方法
    """
    
    @abstractmethod
    def accept(self, visitor):
        """
        接受一个访问者对象并调用相应的visit方法
        
        Args:
            visitor: 访问者对象，实现了StmtVisitor接口
            
        Returns:
            访问者处理语句的结果
        """
        pass


class Expression(Stmt):
    """
    表达式语句
    
    表示一个被用作语句的表达式，如函数调用语句。
    """
    
    def __init__(self, expression):
        """
        初始化表达式语句
        
        Args:
            expression: Expr, 表达式对象
        """
        self.expression = expression
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理语句的结果
        """
        return visitor.visit_expression_stmt(self)


class Print(Stmt):
    """
    打印语句
    
    表示一个打印语句，如'print "Hello, world!";'。
    """
    
    def __init__(self, expression):
        """
        初始化打印语句
        
        Args:
            expression: Expr, 要打印的表达式
        """
        self.expression = expression
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理语句的结果
        """
        return visitor.visit_print_stmt(self)


class Var(Stmt):
    """
    变量声明语句
    
    表示一个变量声明，如'var name = "value";'。
    """
    
    def __init__(self, name, initializer):
        """
        初始化变量声明语句
        
        Args:
            name: Token, 变量名标记
            initializer: Expr, 初始值表达式，可以为None
        """
        self.name = name
        self.initializer = initializer
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理语句的结果
        """
        return visitor.visit_var_stmt(self)


class Block(Stmt):
    """
    块语句
    
    表示一个代码块，包含多个语句。
    例如: { statement1; statement2; }
    """
    
    def __init__(self, statements):
        """
        初始化块语句
        
        Args:
            statements: List[Stmt], 语句列表
        """
        self.statements = statements
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 访问者对象
            
        Returns:
            访问者处理语句的结果
        """
        return visitor.visit_block_stmt(self)


class If(Stmt):
    """
    条件语句
    
    表示条件执行的语句，包含条件表达式和对应的执行分支。
    """
    
    def __init__(self, condition, then_branch, else_branch=None):
        """
        初始化条件语句
        
        Args:
            condition: Expr, 条件表达式
            then_branch: Stmt, 条件为真时执行的语句
            else_branch: Stmt, 条件为假时执行的语句，可以为None
        """
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了visit_if_stmt方法的访问者
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_if_stmt(self)


class While(Stmt):
    """
    while循环语句
    
    表示while循环执行的语句，包含循环条件和循环体。
    """
    
    def __init__(self, condition, body):
        """
        初始化while循环语句
        
        Args:
            condition: Expr, 循环条件表达式
            body: Stmt, 循环体语句
        """
        self.condition = condition
        self.body = body
    
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了visit_while_stmt方法的访问者
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_while_stmt(self)


class Break(Stmt):
    """
    Break语句
    
    中断当前循环的执行。
    
    Attributes:
        keyword: Token, break关键字对应的token
    """
    
    def __init__(self, keyword):
        """
        初始化Break语句
        
        Args:
            keyword: Token, break关键字对应的token
        """
        self.keyword = keyword
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了相应visit方法的访问者
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_break_stmt(self)


class Function(Stmt):
    """
    函数声明语句
    
    表示函数声明，包含函数名称、参数列表和函数体。
    """
    
    def __init__(self, name, params, body, is_static=False, is_getter=False):
        """
        初始化函数声明语句
        
        Args:
            name: Token, 函数名
            params: list, 参数标记列表
            body: list, 函数体语句列表
            is_static: bool, 是否是静态方法
            is_getter: bool, 是否是getter方法
        """
        self.name = name
        self.params = params
        self.body = body
        self.is_static = is_static  # 标记静态方法
        self.is_getter = is_getter  # 标记getter方法
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: Visitor, 访问者对象
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_function_stmt(self)


class Class(Stmt):
    """
    类声明语句
    
    表示一个类声明，包括类名和方法列表。
    """
    
    def __init__(self, name, superclass, methods):
        """
        初始化类声明语句
        
        Args:
            name: Token, 类名标记
            superclass: Variable, 父类变量表达式，可为None
            methods: list, 方法列表
        """
        self.name = name
        self.superclass = superclass
        self.methods = methods
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: StmtVisitor, 访问者
            
        Returns:
            访问者的返回值
        """
        return visitor.visit_class_stmt(self)


class Return(Stmt):
    """
    Return语句
    
    从函数返回值。
    
    Attributes:
        keyword: Token, return关键字
        value: Expr, 返回值表达式
    """
    
    def __init__(self, keyword, value):
        """
        初始化Return语句
        
        Args:
            keyword: Token, return关键字
            value: Expr, 返回值表达式，可以为None
        """
        self.keyword = keyword
        self.value = value
        
    def accept(self, visitor):
        """
        接受访问者
        
        Args:
            visitor: 实现了相应visit方法的访问者
            
        Returns:
            访问者返回的结果
        """
        return visitor.visit_return_stmt(self) 