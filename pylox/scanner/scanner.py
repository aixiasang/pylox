#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .token_type import TokenType
from .token import Token


class Scanner:
    """
    Lox语言的词法分析器
    
    将源代码字符串转换为词法单元(Token)序列。
    """
    
    # 关键字映射
    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "inner": TokenType.INNER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE
    }

    def __init__(self, source):
        """
        初始化扫描器
        
        Args:
            source: str, 源代码字符串
        """
        self.source = source
        self.tokens = []  # 保存已扫描的词法单元
        
        # 追踪当前扫描位置
        self.start = 0  # 当前词法单元起始位置
        self.current = 0  # 当前扫描字符位置
        self.line = 1  # 当前行号

    def scan_tokens(self):
        """
        扫描源代码，生成词法单元
        
        Returns:
            List[Token]: 词法单元列表
        """
        while not self.is_at_end():
            # 开始扫描下一个词法单元
            self.start = self.current
            self.scan_token()
            
        # 添加EOF标记
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def is_at_end(self):
        """
        检查是否到达源代码末尾
        
        Returns:
            bool: 是否到达末尾
        """
        return self.current >= len(self.source)
    
    def scan_token(self):
        """扫描并识别单个词法单元"""
        c = self.advance()
        
        # 处理单字符词法单元
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
            
        # 处理一个或两个字符的词法单元
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            
        # 处理除法和注释
        elif c == '/':
            if self.match('/'):
                # 行注释持续到行末
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                # 块注释 /* ... */
                self.block_comment()
            else:
                self.add_token(TokenType.SLASH)
                
        # 忽略空白字符
        elif c in [' ', '\r', '\t']:
            pass
        # 处理换行
        elif c == '\n':
            self.line += 1
            
        # 处理字符串字面量
        elif c == '"':
            self.string()
            
        # 处理数字字面量和标识符
        else:
            if self.is_digit(c):
                self.number()
            elif self.is_alpha(c):
                self.identifier()
            else:
                # 处理非法字符
                from pylox.lox import Lox
                Lox.error(self.line, f"Unexpected character: {c}")
    
    def advance(self):
        """
        获取当前字符并将指针向前移动
        
        Returns:
            str: 当前字符
        """
        c = self.source[self.current]
        self.current += 1
        return c
    
    def match(self, expected):
        """
        如果下一个字符匹配预期，则消费它
        
        Args:
            expected: str, 预期的下一个字符
            
        Returns:
            bool: 是否匹配
        """
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
            
        self.current += 1
        return True
    
    def peek(self):
        """
        查看当前字符，但不消费它
        
        Returns:
            str: 当前字符，如果到达源码末尾返回'\0'
        """
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        """
        查看下一个字符，但不消费它
        
        Returns:
            str: 下一个字符，如果到达源码末尾返回'\0'
        """
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def string(self):
        """处理字符串字面量"""
        # 找到字符串的闭合引号
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
            
        # 处理未闭合的字符串
        if self.is_at_end():
            from pylox.lox import Lox
            Lox.error(self.line, "Unterminated string.")
            return
            
        # 消费闭合的引号
        self.advance()
        
        # 提取字符串的值（去除引号）
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def number(self):
        """处理数字字面量"""
        # 消费整数部分
        while self.is_digit(self.peek()):
            self.advance()
            
        # 处理小数部分
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # 消费小数点
            self.advance()
            
            # 消费小数部分
            while self.is_digit(self.peek()):
                self.advance()
                
        # 添加数字词法单元
        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)
    
    def identifier(self):
        """处理标识符和关键字"""
        while self.is_alphanumeric(self.peek()):
            self.advance()
            
        # 检查是否为关键字
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        
        self.add_token(token_type)
    
    def is_digit(self, c):
        """
        检查字符是否为数字
        
        Args:
            c: str, 要检查的字符
            
        Returns:
            bool: 是否为数字
        """
        return '0' <= c <= '9'
    
    def is_alpha(self, c):
        """
        检查字符是否为字母或下划线
        
        Args:
            c: str, 要检查的字符
            
        Returns:
            bool: 是否为字母或下划线
        """
        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_'
    
    def is_alphanumeric(self, c):
        """
        检查字符是否为字母、数字或下划线
        
        Args:
            c: str, 要检查的字符
            
        Returns:
            bool: 是否为字母、数字或下划线
        """
        return self.is_alpha(c) or self.is_digit(c)
    
    def block_comment(self):
        """处理C风格的块注释 /* ... */，支持嵌套"""
        # 记录嵌套层级
        nesting_level = 1
        
        while nesting_level > 0 and not self.is_at_end():
            if self.peek() == '/' and self.peek_next() == '*':
                # 发现嵌套块注释的开始
                self.advance()  # 消费 '/'
                self.advance()  # 消费 '*'
                nesting_level += 1
            elif self.peek() == '*' and self.peek_next() == '/':
                # 发现块注释的结束
                self.advance()  # 消费 '*'
                self.advance()  # 消费 '/'
                nesting_level -= 1
            elif self.peek() == '\n':
                # 处理换行
                self.advance()
                self.line += 1
            else:
                # 消费其他字符
                self.advance()
        
        # 如果在源代码结束前没有关闭块注释
        if self.is_at_end() and nesting_level > 0:
            from pylox.lox import Lox
            Lox.error(self.line, "Unterminated block comment.")
    
    def add_token(self, token_type, literal=None):
        """
        添加词法单元到结果列表
        
        Args:
            token_type: TokenType, 词法单元类型
            literal: 可选，字面量的值
        """
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))