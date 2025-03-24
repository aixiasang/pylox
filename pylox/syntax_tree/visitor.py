#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
访问者模式接口，用于操作语法树
"""

from abc import ABC, abstractmethod


class Visitor(ABC):
    """
    表达式访问者抽象基类
    
    实现访问者模式，允许在不修改表达式类的情况下添加新的操作。
    每个具体访问者类必须为每种表达式类型实现一个visit方法。
    """
    
    @abstractmethod
    def visit_binary_expr(self, expr):
        """处理二元表达式"""
        pass
    
    @abstractmethod
    def visit_grouping_expr(self, expr):
        """处理分组表达式"""
        pass
    
    @abstractmethod
    def visit_literal_expr(self, expr):
        """处理字面量表达式"""
        pass
    
    @abstractmethod
    def visit_unary_expr(self, expr):
        """处理一元表达式"""
        pass
    
    @abstractmethod
    def visit_variable_expr(self, expr):
        """处理变量表达式"""
        pass
    
    @abstractmethod
    def visit_assign_expr(self, expr):
        """处理赋值表达式"""
        pass
    
    @abstractmethod
    def visit_logical_expr(self, expr):
        """处理逻辑表达式"""
        pass
    
    @abstractmethod
    def visit_call_expr(self, expr):
        """处理函数调用表达式"""
        pass
    
    @abstractmethod
    def visit_lambda_expr(self, expr):
        """处理Lambda表达式"""
        pass
    
    @abstractmethod
    def visit_expression_stmt(self, stmt):
        """处理表达式语句"""
        pass
    
    @abstractmethod
    def visit_print_stmt(self, stmt):
        """处理打印语句"""
        pass
    
    @abstractmethod
    def visit_var_stmt(self, stmt):
        """处理变量声明语句"""
        pass
    
    @abstractmethod
    def visit_block_stmt(self, stmt):
        """处理块语句"""
        pass
    
    @abstractmethod
    def visit_if_stmt(self, stmt):
        """处理if语句"""
        pass
    
    @abstractmethod
    def visit_while_stmt(self, stmt):
        """处理while语句"""
        pass
    
    @abstractmethod
    def visit_break_stmt(self, stmt):
        """处理break语句"""
        pass
    
    @abstractmethod
    def visit_function_stmt(self, stmt):
        """处理函数声明语句"""
        pass
    
    @abstractmethod
    def visit_return_stmt(self, stmt):
        """处理return语句"""
        pass