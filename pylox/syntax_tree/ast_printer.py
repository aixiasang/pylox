#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
抽象语法树打印器

提供了一种将抽象语法树转换为可读字符串表示的方法，
用于调试和可视化语法树结构。
"""

from .visitor import Visitor


class AstPrinter(Visitor):
    """
    将表达式树转换为括号表示法的字符串
    
    例如，表达式 "1 + 2 * 3" 会转换为:
    "(+ 1 (* 2 3))"
    """
    
    def print(self, expr):
        """
        将表达式打印为字符串
        
        Args:
            expr: Expr, 要打印的表达式
            
        Returns:
            str: 表达式的括号表示法字符串
        """
        return expr.accept(self)
    
    def visit_binary_expr(self, expr):
        """
        访问二元表达式
        
        Args:
            expr: Binary, 二元表达式
            
        Returns:
            str: 括号表示法字符串
        """
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_grouping_expr(self, expr):
        """
        访问分组表达式
        
        Args:
            expr: Grouping, 分组表达式
            
        Returns:
            str: 括号表示法字符串
        """
        return self._parenthesize("group", expr.expression)
    
    def visit_literal_expr(self, expr):
        """
        访问字面量表达式
        
        Args:
            expr: Literal, 字面量表达式
            
        Returns:
            str: 字面量的字符串表示
        """
        if expr.value is None:
            return "nil"
        return str(expr.value)
    
    def visit_unary_expr(self, expr):
        """
        访问一元表达式
        
        Args:
            expr: Unary, 一元表达式
            
        Returns:
            str: 括号表示法字符串
        """
        return self._parenthesize(expr.operator.lexeme, expr.right)
    
    def visit_variable_expr(self, expr):
        """
        访问变量表达式
        
        Args:
            expr: Variable, 变量表达式
            
        Returns:
            str: 变量名
        """
        return expr.name.lexeme
    
    def visit_assign_expr(self, expr):
        """
        访问赋值表达式
        
        Args:
            expr: Assign, 赋值表达式
            
        Returns:
            str: 括号表示法字符串
        """
        return self._parenthesize("=", expr.name.lexeme, expr.value)
    
    def visit_expression_stmt(self, stmt):
        """
        访问表达式语句
        
        Args:
            stmt: Expression, 表达式语句
            
        Returns:
            str: 括号表示法字符串
        """
        return self._parenthesize("expr", stmt.expression)
    
    def visit_print_stmt(self, stmt):
        """
        访问打印语句
        
        Args:
            stmt: Print, 打印语句
            
        Returns:
            str: 括号表示法字符串
        """
        return self._parenthesize("print", stmt.expression)
    
    def visit_var_stmt(self, stmt):
        """
        访问变量声明语句
        
        Args:
            stmt: Var, 变量声明语句
            
        Returns:
            str: 括号表示法字符串
        """
        if stmt.initializer:
            return self._parenthesize("var", stmt.name.lexeme, stmt.initializer)
        return self._parenthesize("var", stmt.name.lexeme)
    
    def visit_block_stmt(self, stmt):
        """
        访问块语句
        
        Args:
            stmt: Block, 块语句
            
        Returns:
            str: 括号表示法字符串
        """
        exprs = []
        for statement in stmt.statements:
            exprs.append(statement)
        return self._parenthesize("block", *exprs)
    
    def visit_call_expr(self, expr):
        """
        访问函数调用表达式
        
        Args:
            expr: Call, 函数调用表达式
            
        Returns:
            str: 该表达式的字符串表示
        """
        return self._parenthesize("call", expr.callee, *expr.arguments)
    
    def visit_lambda_expr(self, expr):
        """
        访问Lambda表达式
        
        Args:
            expr: Lambda, Lambda表达式
            
        Returns:
            str: 该表达式的字符串表示
        """
        params = []
        for param in expr.params:
            params.append(param.lexeme)
            
        return self._parenthesize("lambda", *params)
    
    def visit_logical_expr(self, expr):
        """
        访问逻辑表达式
        
        Args:
            expr: Logical, 逻辑表达式
            
        Returns:
            str: 该表达式的字符串表示
        """
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visit_if_stmt(self, stmt):
        """
        访问if语句
        
        Args:
            stmt: If, if语句
            
        Returns:
            str: 该语句的字符串表示
        """
        if stmt.else_branch:
            return self._parenthesize("if-else", stmt.condition, stmt.then_branch, stmt.else_branch)
        return self._parenthesize("if", stmt.condition, stmt.then_branch)
    
    def visit_while_stmt(self, stmt):
        """
        访问while语句
        
        Args:
            stmt: While, while语句
            
        Returns:
            str: 该语句的字符串表示
        """
        return self._parenthesize("while", stmt.condition, stmt.body)
    
    def visit_break_stmt(self, stmt):
        """
        访问break语句
        
        Args:
            stmt: Break, break语句
            
        Returns:
            str: 该语句的字符串表示
        """
        return self._parenthesize("break")
    
    def visit_function_stmt(self, stmt):
        """
        访问函数声明语句
        
        Args:
            stmt: Function, 函数声明语句
            
        Returns:
            str: 该语句的字符串表示
        """
        params = []
        for param in stmt.params:
            params.append(param.lexeme)
        
        body_parts = []
        for statement in stmt.body:
            body_parts.append(statement.accept(self))
        body_str = "(" + " ".join(["block"] + body_parts) + ")"
        
        return self._parenthesize("fun " + stmt.name.lexeme, *params) + " " + body_str
    
    def visit_return_stmt(self, stmt):
        """
        访问return语句
        
        Args:
            stmt: Return, return语句
            
        Returns:
            str: 该语句的字符串表示
        """
        if stmt.value:
            return self._parenthesize("return", stmt.value)
        return self._parenthesize("return")
    
    def _parenthesize(self, name, *exprs):
        """
        将表达式和名称格式化为括号表示法
        
        Args:
            name: str, 表达式名称（如运算符）
            *exprs: 表达式对象列表或字符串
            
        Returns:
            str: 格式化后的括号表示法字符串
        """
        builder = []
        
        builder.append("(")
        builder.append(name)
        
        for expr in exprs:
            builder.append(" ")
            if isinstance(expr, str):
                builder.append(expr)
            else:
                builder.append(expr.accept(self))
            
        builder.append(")")
        
        return "".join(builder)