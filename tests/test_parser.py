#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试解析器功能
"""

import unittest
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.syntax_tree import AstPrinter, Binary, Grouping, Literal, Unary


class TestParser(unittest.TestCase):
    """测试解析器功能"""
    
    def setUp(self):
        """测试前准备"""
        # 重置错误状态
        from pylox.lox import Lox
        Lox.had_error = False
    
    def parse_expression(self, source):
        """
        解析给定源码的表达式
        
        Args:
            source: str, 要解析的源代码
            
        Returns:
            解析后的表达式对象
        """
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        parser = Parser(tokens)
        return parser.parse_expression()
    
    def test_basic_expressions(self):
        """测试基本表达式"""
        # 测试数字字面量
        expr = self.parse_expression("123")
        self.assertIsInstance(expr, Literal)
        self.assertEqual(expr.value, 123.0)
        
        # 测试字符串字面量
        expr = self.parse_expression("\"hello\"")
        self.assertIsInstance(expr, Literal)
        self.assertEqual(expr.value, "hello")
        
        # 测试布尔值
        expr = self.parse_expression("true")
        self.assertIsInstance(expr, Literal)
        self.assertEqual(expr.value, True)
        
        expr = self.parse_expression("false")
        self.assertIsInstance(expr, Literal)
        self.assertEqual(expr.value, False)
        
        # 测试nil
        expr = self.parse_expression("nil")
        self.assertIsInstance(expr, Literal)
        self.assertIsNone(expr.value)
    
    def test_unary_expressions(self):
        """测试一元表达式"""
        # 测试负号
        expr = self.parse_expression("-123")
        self.assertIsInstance(expr, Unary)
        self.assertEqual(expr.operator.lexeme, "-")
        self.assertIsInstance(expr.right, Literal)
        self.assertEqual(expr.right.value, 123.0)
        
        # 测试逻辑非
        expr = self.parse_expression("!true")
        self.assertIsInstance(expr, Unary)
        self.assertEqual(expr.operator.lexeme, "!")
        self.assertIsInstance(expr.right, Literal)
        self.assertEqual(expr.right.value, True)
    
    def test_binary_expressions(self):
        """测试二元表达式"""
        # 测试加法
        expr = self.parse_expression("1 + 2")
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.lexeme, "+")
        self.assertIsInstance(expr.left, Literal)
        self.assertEqual(expr.left.value, 1.0)
        self.assertIsInstance(expr.right, Literal)
        self.assertEqual(expr.right.value, 2.0)
        
        # 测试乘法
        expr = self.parse_expression("3 * 4")
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.lexeme, "*")
        self.assertEqual(expr.left.value, 3.0)
        self.assertEqual(expr.right.value, 4.0)
    
    def test_comparison_expressions(self):
        """测试比较表达式"""
        # 测试小于
        expr = self.parse_expression("1 < 2")
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.lexeme, "<")
        
        # 测试大于等于
        expr = self.parse_expression("3 >= 4")
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.lexeme, ">=")
        
        # 测试等于
        expr = self.parse_expression("5 == 5")
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.lexeme, "==")
        
        # 测试不等于
        expr = self.parse_expression("6 != 7")
        self.assertIsInstance(expr, Binary)
        self.assertEqual(expr.operator.lexeme, "!=")
    
    def test_grouping_expressions(self):
        """测试分组表达式"""
        expr = self.parse_expression("(1 + 2)")
        self.assertIsInstance(expr, Grouping)
        self.assertIsInstance(expr.expression, Binary)
        self.assertEqual(expr.expression.operator.lexeme, "+")
    
    def test_complex_expressions(self):
        """测试复杂表达式"""
        # 测试优先级：乘法优先级高于加法
        expr = self.parse_expression("1 + 2 * 3")
        
        printer = AstPrinter()
        result = printer.print(expr)
        
        # 应该解析为：(+ 1 (* 2 3))，而不是：(* (+ 1 2) 3)
        self.assertEqual(result, "(+ 1.0 (* 2.0 3.0))")
        
        # 测试复杂组合
        expr = self.parse_expression("(1 + 2) * (3 - 4) / -5")
        
        # 预期： (/ (* (group (+ 1 2)) (group (- 3 4))) (- 5))
        result = printer.print(expr)
        expected = "(/ (* (group (+ 1.0 2.0)) (group (- 3.0 4.0))) (- 5.0))"
        self.assertEqual(result, expected)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试未闭合的括号
        expr = self.parse_expression("(1 + 2")
        self.assertIsNone(expr)
        
        from pylox.lox import Lox
        self.assertTrue(Lox.had_error)
        
        # 重置错误状态
        Lox.had_error = False
        
        # 测试缺少右操作数
        expr = self.parse_expression("1 +")
        self.assertIsNone(expr)
        self.assertTrue(Lox.had_error)


if __name__ == "__main__":
    unittest.main()