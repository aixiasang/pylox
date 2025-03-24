#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pylox.syntax_tree import Expr, Binary, Grouping, Literal, Unary, AstPrinter
from pylox.scanner.token import Token
from pylox.scanner.token_type import TokenType


class TestAst(unittest.TestCase):
    """测试抽象语法树功能"""
    
    def test_ast_printer(self):
        """测试AST打印器"""
        # 创建表达式: -123 * (45.67)
        expression = Binary(
            Unary(
                Token(TokenType.MINUS, "-", None, 1),
                Literal(123)
            ),
            Token(TokenType.STAR, "*", None, 1),
            Grouping(
                Literal(45.67)
            )
        )
        
        printer = AstPrinter()
        result = printer.print(expression)
        
        # 预期输出: "(* (- 123) (group 45.67))"
        self.assertEqual(result, "(* (- 123) (group 45.67))")
    
    def test_complex_expression(self):
        """测试更复杂的表达式"""
        # 创建表达式: 1 + 2 * 3 - 4 / 5
        # 注意：这里没有考虑操作符优先级，仅作为AST测试
        expression = Binary(
            Binary(
                Literal(1),
                Token(TokenType.PLUS, "+", None, 1),
                Binary(
                    Literal(2),
                    Token(TokenType.STAR, "*", None, 1),
                    Literal(3)
                )
            ),
            Token(TokenType.MINUS, "-", None, 1),
            Binary(
                Literal(4),
                Token(TokenType.SLASH, "/", None, 1),
                Literal(5)
            )
        )
        
        printer = AstPrinter()
        result = printer.print(expression)
        
        # 预期输出: "(- (+ 1 (* 2 3)) (/ 4 5))"
        self.assertEqual(result, "(- (+ 1 (* 2 3)) (/ 4 5))")
    
    def test_literal_expressions(self):
        """测试各种字面量表达式"""
        # 数字
        self.assertEqual(AstPrinter().print(Literal(42)), "42")
        
        # 字符串
        self.assertEqual(AstPrinter().print(Literal("hello")), "hello")
        
        # 布尔值
        self.assertEqual(AstPrinter().print(Literal(True)), "True")
        self.assertEqual(AstPrinter().print(Literal(False)), "False")
        
        # 空值
        self.assertEqual(AstPrinter().print(Literal(None)), "nil")


if __name__ == "__main__":
    unittest.main()