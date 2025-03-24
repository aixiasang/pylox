#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pylox.scanner import Scanner, Token, TokenType


class TestScanner(unittest.TestCase):
    """测试扫描器功能"""
    
    def test_empty_source(self):
        """测试空源代码"""
        scanner = Scanner("")
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_whitespace(self):
        """测试空白字符"""
        scanner = Scanner(" \t\r\n")
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_single_character_tokens(self):
        """测试单字符词法单元"""
        source = "(){},.-+;*"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有10个token
        self.assertEqual(len(tokens), 10 + 1)
        
        # 验证每个token的类型
        self.assertEqual(tokens[0].type, TokenType.LEFT_PAREN)
        self.assertEqual(tokens[1].type, TokenType.RIGHT_PAREN)
        self.assertEqual(tokens[2].type, TokenType.LEFT_BRACE)
        self.assertEqual(tokens[3].type, TokenType.RIGHT_BRACE)
        self.assertEqual(tokens[4].type, TokenType.COMMA)
        self.assertEqual(tokens[5].type, TokenType.DOT)
        self.assertEqual(tokens[6].type, TokenType.MINUS)
        self.assertEqual(tokens[7].type, TokenType.PLUS)
        self.assertEqual(tokens[8].type, TokenType.SEMICOLON)
        self.assertEqual(tokens[9].type, TokenType.STAR)
    
    def test_one_or_two_character_tokens(self):
        """测试一个或两个字符的词法单元"""
        source = "! != = == > >= < <="
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有8个token
        self.assertEqual(len(tokens), 8 + 1)
        
        # 验证每个token的类型
        self.assertEqual(tokens[0].type, TokenType.BANG)
        self.assertEqual(tokens[1].type, TokenType.BANG_EQUAL)
        self.assertEqual(tokens[2].type, TokenType.EQUAL)
        self.assertEqual(tokens[3].type, TokenType.EQUAL_EQUAL)
        self.assertEqual(tokens[4].type, TokenType.GREATER)
        self.assertEqual(tokens[5].type, TokenType.GREATER_EQUAL)
        self.assertEqual(tokens[6].type, TokenType.LESS)
        self.assertEqual(tokens[7].type, TokenType.LESS_EQUAL)
    
    def test_strings(self):
        """测试字符串字面量"""
        source = '"Hello, world!" "Another string"'
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有2个token
        self.assertEqual(len(tokens), 2 + 1)
        
        # 验证token类型和字面量值
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "Hello, world!")
        
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].literal, "Another string")
    
    def test_numbers(self):
        """测试数字字面量"""
        source = "123 123.456"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有2个token
        self.assertEqual(len(tokens), 2 + 1)
        
        # 验证token类型和字面量值
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].literal, 123.0)
        
        self.assertEqual(tokens[1].type, TokenType.NUMBER)
        self.assertEqual(tokens[1].literal, 123.456)
    
    def test_identifiers_and_keywords(self):
        """测试标识符和关键字"""
        source = "identifier var if else while for class"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有7个token
        self.assertEqual(len(tokens), 7 + 1)
        
        # 验证token类型
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[1].type, TokenType.VAR)
        self.assertEqual(tokens[2].type, TokenType.IF)
        self.assertEqual(tokens[3].type, TokenType.ELSE)
        self.assertEqual(tokens[4].type, TokenType.WHILE)
        self.assertEqual(tokens[5].type, TokenType.FOR)
        self.assertEqual(tokens[6].type, TokenType.CLASS)
    
    def test_line_comments(self):
        """测试行注释"""
        source = "// This is a comment\nvar a = 5;"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有5个token (var, a, =, 5, ;)
        self.assertEqual(len(tokens), 5 + 1)
        
        # 验证token类型
        self.assertEqual(tokens[0].type, TokenType.VAR)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].type, TokenType.EQUAL)
        self.assertEqual(tokens[3].type, TokenType.NUMBER)
        self.assertEqual(tokens[4].type, TokenType.SEMICOLON)
        
    def test_block_comments(self):
        """测试块注释"""
        source = "/* This is a block comment */\nvar a = 5;"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有5个token (var, a, =, 5, ;)
        self.assertEqual(len(tokens), 5 + 1)
        
        # 验证token类型
        self.assertEqual(tokens[0].type, TokenType.VAR)
        self.assertEqual(tokens[1].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].type, TokenType.EQUAL)
        self.assertEqual(tokens[3].type, TokenType.NUMBER)
        self.assertEqual(tokens[4].type, TokenType.SEMICOLON)
        
    def test_multiline_block_comments(self):
        """测试多行块注释"""
        source = "/* This is\n a multiline\n block comment */\nvar a = 5;"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有5个token (var, a, =, 5, ;)
        self.assertEqual(len(tokens), 5 + 1)
        
        # 验证token类型
        self.assertEqual(tokens[0].type, TokenType.VAR)
        
    def test_nested_block_comments(self):
        """测试嵌套块注释"""
        source = "/* Outer comment /* Nested comment */ still in outer */\nvar a = 5;"
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证除了EOF外有5个token (var, a, =, 5, ;)
        self.assertEqual(len(tokens), 5 + 1)
        
        # 验证token类型
        self.assertEqual(tokens[0].type, TokenType.VAR)
        
    def test_unterminated_block_comment(self):
        """测试未闭合的块注释"""
        # 源代码结束前未闭合块注释
        source = "/* This comment is not closed\nvar a = 5;"
        
        # 记录原来的错误状态
        from pylox.lox import Lox
        had_error = Lox.had_error
        
        # 运行测试
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 验证是否正确报告了错误
        self.assertTrue(Lox.had_error)
        
        # 重置错误状态
        Lox.had_error = had_error


if __name__ == "__main__":
    unittest.main()