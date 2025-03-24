#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化的解析器实现

使用数组索引代替映射查找，提高性能。
"""

from pylox.syntax_tree.visitor import Visitor


class OptimizedResolver(Visitor):
    """
    优化的变量解析器
    
    使用数组索引代替映射查找，提高变量访问性能。
    """
    
    def __init__(self, interpreter):
        """
        初始化解析器
        
        Args:
            interpreter: Interpreter, 解释器实例，用于存储解析结果
        """
        self.interpreter = interpreter
        self.scopes = []  # 作用域栈
        self.current_function = 0  # 当前函数类型
        self.warn_unused = True  # 是否警告未使用的变量
        
        # 优化：为每个局部变量分配唯一索引
        self.locals = {}  # 变量名到索引的映射
        self.next_index = 0  # 下一个可用索引
    
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
        # 优化：每个作用域包含变量名到索引的映射
        self.scopes.append({})
    
    def end_scope(self):
        """结束当前作用域，检查未使用的变量"""
        if self.warn_unused and self.scopes:
            scope = self.scopes[-1]
            from pylox.lox import Lox
            
            # 检查作用域中是否有未使用的变量
            for name, (initialized, used, _) in scope.items():
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
        
        # 分配新的索引
        index = self.next_index
        self.next_index += 1
        
        # 变量状态：[是否已初始化, 是否已使用, 索引]
        scope[name.lexeme] = [False, False, index]
    
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
                
                # 获取变量索引
                index = self.scopes[i][name.lexeme][2]
                
                # 存储距离和索引
                depth = len(self.scopes) - 1 - i
                self.interpreter.resolve_optimized(expr, depth, index)
                return
        
        # 变量未找到，可能是全局变量，让解释器处理
    
    def resolve_function(self, function, type):
        """
        解析函数声明
        
        Args:
            function: Function, 函数声明
            type: int, 函数类型
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
        self.resolve_function(stmt, 1)  # 1表示函数
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
        if self.current_function == 0:
            from pylox.lox import Lox
            Lox.error(stmt.keyword, "不能在函数外部使用return语句。")
        
        if stmt.value is not None:
            self.resolve_expr(stmt.value)
        
        return None
    
    def visit_var_stmt(self, stmt):
        """访问变量声明语句"""
        self.declare(stmt.name)
        
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        
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
        """访问变量表达式"""
        # 检查变量是否引用了它自己的初始化器
        if self.scopes and expr.name.lexeme in self.scopes[-1] and self.scopes[-1][expr.name.lexeme][0] == False:
            from pylox.lox import Lox
            Lox.error(expr.name, "不能在变量自己的初始化器中引用该变量。")
        
        # 解析变量引用
        self.resolve_local(expr, expr.name)
        return None
    
    def visit_lambda_expr(self, expr):
        """访问Lambda表达式"""
        # 处理匿名函数表达式
        self.resolve_function(expr, 1)
        return None