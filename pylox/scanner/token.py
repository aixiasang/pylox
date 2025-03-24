#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Token:
    """
    表示Lox语言中的词法单元
    
    一个词法单元包含类型、词素、字面量值和行号信息。
    """
    
    def __init__(self, token_type, lexeme, literal, line):
        """
        初始化Token对象
        
        Args:
            token_type: TokenType 枚举值，表示词法单元类型
            lexeme: str, 原始词素字符串
            literal: 任意类型，字面量的值（如果有）
            line: int, 词法单元在源码中的行号
        """
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        """字符串表示，用于打印Token"""
        return f"{self.type} {self.lexeme} {self.literal}"
        
    def __repr__(self):
        """对象的正式字符串表示"""
        return f"Token({self.type}, '{self.lexeme}', {self.literal}, {self.line})"