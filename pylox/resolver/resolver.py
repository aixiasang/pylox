#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
解析器实现

处理词法作用域的变量解析，在解释器执行前进行静态分析。
解决闭包中变量绑定的问题。
"""

from pylox.syntax_tree.visitor import Visitor
from pylox.syntax_tree.expr import Variable


# 函数类型枚举
class FunctionType:
    """函数类型枚举"""
    
    NONE = 0      # 不在函数内
    FUNCTION = 1  # 在普通函数内
    INITIALIZER = 2  # 在初始化方法内
    METHOD = 3    # 在方法内


# 类类型枚举
class ClassType:
    """类类型枚举"""
    
    NONE = 0     # 不在类内
    CLASS = 1    # 在类内


class Resolver(Visitor):
    """
    变量解析器
    
    遍历AST，解析变量引用，确保它们绑定到正确的声明。
    实现了访问者模式接口。
    """
    
    def __init__(self, interpreter):
        """
        初始化解析器
        
        Args:
            interpreter: Interpreter, 解释器实例，用于存储解析结果
        """
        self.interpreter = interpreter
        self.scopes = []  # 作用域栈
        self.current_function = FunctionType.NONE  # 当前函数类型
        self.current_class = ClassType.NONE  # 当前类类型
        self.warn_unused = True  # 是否警告未使用的变量
        # 特殊标记，当解析变量声明时，暂时允许引用外部同名变量
        self.in_var_declaration = False  
        # 当前正在声明的变量名
        self.current_var_name = None
        from pylox.lox import Lox
        self.lox = Lox  # Lox类引用，用于错误报告
    
    def resolve(self, statements):
        """
        解析语句列表
        
        Args:
            statements: list[Stmt], 语句列表
        """
        if isinstance(statements, list):
            for statement in statements:
                self.resolve_stmt(statement)
        else:
            # 单个语句或表达式
            self.resolve_stmt(statements)
    
    def resolve_stmt(self, stmt):
        """
        解析单个语句
        
        Args:
            stmt: Stmt, 语句对象
        """
        stmt.accept(self)
    
    def resolve_expr(self, expr):
        """
        解析单个表达式
        
        Args:
            expr: Expr, 表达式对象
        """
        expr.accept(self)
    
    def begin_scope(self):
        """开始一个新的作用域"""
        self.scopes.append({})
    
    def end_scope(self):
        """结束当前作用域，检查未使用的变量"""
        if self.warn_unused and self.scopes:
            scope = self.scopes[-1]
            from pylox.lox import Lox
            
            # 检查作用域中是否有未使用的变量
            for name, [initialized, used] in scope.items():
                if not used and initialized:
                    Lox.warning(f"局部变量 '{name}' 已声明但从未使用。")
        
        self.scopes.pop()
    
    def declare(self, name):
        """
        声明变量
        
        Args:
            name: Token, 变量名标记
        """
        if not self.scopes:
            return  # 全局作用域，不需要解析
        
        scope = self.scopes[-1]
        
        # 检查变量是否已在当前作用域中声明
        if name.lexeme in scope:
            from pylox.lox import Lox
            Lox.error(name, f"已经在此作用域中声明了变量'{name.lexeme}'。")
        
        # 变量状态：[是否已初始化, 是否已使用]
        scope[name.lexeme] = [False, False]
    
    def define(self, name):
        """
        定义变量(初始化)
        
        Args:
            name: Token, 变量名标记
        """
        if not self.scopes:
            return  # 全局作用域，不需要解析
        
        # 标记为"已初始化"
        self.scopes[-1][name.lexeme][0] = True
    
    def mark_used(self, name):
        """
        标记变量已被使用
        
        Args:
            name: str, 变量名
        """
        # 从内到外检查作用域
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name][1] = True
                return
    
    def resolve_local(self, expr, name):
        """
        解析局部变量
        
        Args:
            expr: Expr, 表达式对象
            name: Token, 变量名标记
        """
        # 从内到外查找变量声明
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                # 标记变量为已使用
                self.scopes[i][name.lexeme][1] = True
                # 找到变量，确定它在作用域栈中的深度
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
        
        # 变量未找到，可能是全局变量，让解释器处理
    
    def resolve_function(self, function, type):
        """
        解析函数声明
        
        Args:
            function: Function, 函数声明
            type: FunctionType, 函数类型
        """
        enclosing_function = self.current_function
        self.current_function = type
        
        # 为函数创建新的作用域
        self.begin_scope()
        
        # 声明并定义参数
        for param in function.params:
            self.declare(param)
            self.define(param)
        
        # 解析函数体
        self.resolve(function.body)
        
        # 结束函数作用域
        self.end_scope()
        
        # 恢复函数类型
        self.current_function = enclosing_function
    
    # 访问方法实现
    def visit_block_stmt(self, stmt):
        """访问块语句"""
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None
    
    def visit_expression_stmt(self, stmt):
        """访问表达式语句"""
        self.resolve_expr(stmt.expression)
        return None
    
    def visit_function_stmt(self, stmt):
        """访问函数声明语句"""
        # 先声明函数名，允许递归引用
        self.declare(stmt.name)
        self.define(stmt.name)
        
        # 解析函数体
        self.resolve_function(stmt, FunctionType.FUNCTION)
        return None
    
    def visit_if_stmt(self, stmt):
        """访问if语句"""
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_stmt(stmt.else_branch)
        return None
    
    def visit_print_stmt(self, stmt):
        """访问打印语句"""
        self.resolve_expr(stmt.expression)
        return None
    
    def visit_return_stmt(self, stmt):
        """访问return语句"""
        # 检查return语句是否在函数内部
        if self.current_function == FunctionType.NONE:
            from pylox.lox import Lox
            Lox.error(stmt.keyword, "不能在函数外部使用return语句。")
        
        if stmt.value is not None:
            self.resolve_expr(stmt.value)
        
        return None
    
    def find_variable_in_outer_scope(self, name):
        """
        在外部作用域中查找变量
        
        Args:
            name: str, 变量名
            
        Returns:
            int: 如果找到，返回变量所在的作用域深度；否则返回-1
        """
        # 从倒数第二个作用域开始查找
        for i in range(len(self.scopes) - 2, -1, -1):
            if name in self.scopes[i]:
                return i
        return -1
        
    def visit_var_stmt(self, stmt):
        """访问变量声明语句"""
        # 先在当前作用域中声明变量
        self.declare(stmt.name)
        
        # 设置正在声明变量的状态
        old_in_var_declaration = self.in_var_declaration
        old_current_var_name = self.current_var_name
        self.in_var_declaration = True
        self.current_var_name = stmt.name.lexeme
        
        try:
            # 如果有初始化表达式，解析它
            if stmt.initializer is not None:
                self.resolve_expr(stmt.initializer)
        finally:
            # 恢复状态
            self.in_var_declaration = old_in_var_declaration
            self.current_var_name = old_current_var_name
        
        # 变量初始化完成后标记为已定义
        self.define(stmt.name)
        return None
    
    def visit_while_stmt(self, stmt):
        """访问while语句"""
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)
        return None
    
    def visit_break_stmt(self, stmt):
        """访问break语句"""
        return None
    
    def visit_assign_expr(self, expr):
        """访问赋值表达式"""
        # 先解析右侧表达式
        self.resolve_expr(expr.value)
        # 解析变量引用
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_binary_expr(self, expr):
        """访问二元表达式"""
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None
    
    def visit_call_expr(self, expr):
        """访问函数调用表达式"""
        self.resolve_expr(expr.callee)
        
        for argument in expr.arguments:
            self.resolve_expr(argument)
        
        return None
    
    def visit_grouping_expr(self, expr):
        """访问分组表达式"""
        self.resolve_expr(expr.expression)
        return None
    
    def visit_literal_expr(self, expr):
        """访问字面量表达式"""
        return None  # 字面量不需要解析
    
    def visit_logical_expr(self, expr):
        """访问逻辑表达式"""
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)
        return None
    
    def visit_unary_expr(self, expr):
        """访问一元表达式"""
        self.resolve_expr(expr.right)
        return None
    
    def visit_variable_expr(self, expr):
        """访问变量表达式，确保变量已定义，并解析到其所在环境的位置"""
        # check if variable exists in the current scope and is being initialized
        if self.scopes and expr.name.lexeme in self.scopes[-1]:
            initialized = self.scopes[-1][expr.name.lexeme]
            if not initialized:
                # 检查是否可能引用的是外部作用域的同名变量
                for scope in reversed(self.scopes[:-1]):
                    if expr.name.lexeme in scope and scope[expr.name.lexeme]:
                        # 变量在外部作用域已初始化，不算自引用
                        break
                else:
                    # 没找到外部作用域的同名变量，确认是自引用错误
                    from pylox.lox import Lox
                    Lox.error(expr.name, "不能在变量自己的初始化器中引用该变量。")
                
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_lambda_expr(self, expr):
        """访问Lambda表达式"""
        # 处理匿名函数表达式
        self.resolve_function(expr, FunctionType.FUNCTION)
        return None

    def visit_class_stmt(self, stmt):
        """
        访问类声明语句
        
        Args:
            stmt: Class, 类声明语句
            
        Returns:
            None
        """
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        
        self.declare(stmt.name)
        self.define(stmt.name)
        
        # 处理继承
        if stmt.superclass is not None:
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                self.lox.error(stmt.superclass.name, "类不能继承自身。")
            
            self.resolve_expr(stmt.superclass)
            
            # 为super创建一个新的作用域
            self.begin_scope()
            self.scopes[-1]["super"] = [True, True]
        
        # 创建一个新的作用域用于this
        self.begin_scope()
        self.scopes[-1]["this"] = [True, True]  # this总是已初始化和已使用
        
        # 解析方法
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            # 如果是初始化方法
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
                
            self.resolve_function(method, declaration)
            
        # 关闭this作用域
        self.end_scope()
        
        # 如果有继承，关闭super作用域
        if stmt.superclass is not None:
            self.end_scope()
        
        self.current_class = enclosing_class
        return None

    def visit_get_expr(self, expr):
        """
        访问属性访问表达式
        
        Args:
            expr: Get, 属性访问表达式
            
        Returns:
            None
        """
        self.resolve_expr(expr.object)
        return None
    
    def visit_set_expr(self, expr):
        """
        访问属性设置表达式
        
        Args:
            expr: Set, 属性设置表达式
            
        Returns:
            None
        """
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.object)
        return None
    
    def visit_this_expr(self, expr):
        """
        访问this表达式
        
        Args:
            expr: This, this表达式
            
        Returns:
            None
        """
        if self.current_class == ClassType.NONE:
            from pylox.lox import Lox
            self.lox = Lox
            Lox.error(expr.keyword, "无法在类外部使用'this'。")
            return None
            
        self.resolve_local(expr, expr.keyword)
        return None

    def visit_super_expr(self, expr):
        """
        访问super表达式
        
        Args:
            expr: Super, super表达式
            
        Returns:
            None
        """
        # 检查是否在类中
        if self.current_class == ClassType.NONE:
            self.lox.error(expr.keyword, "不能在类外部使用'super'。")
        
        # 解析super关键字
        self.resolve_local(expr, expr.keyword)
        return None