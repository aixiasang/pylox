#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lox解释器的主类

提供运行Lox代码的公共接口和错误处理功能。
"""

import sys
import os
import traceback
import time
import re
import copy
from io import StringIO
import types
import inspect
import importlib

# 解决ast命名冲突
import ast as python_stdlib_ast

# 确保优先使用Python标准库模块
for i in range(len(sys.path)-1, -1, -1):
    if "site-packages" in sys.path[i]:
        sys.path.insert(0, sys.path.pop(i))

# 使用标准库的ast模块，避免与项目冲突
from pylox.scanner import Scanner, TokenType
from pylox.interpreter.runtime_error import RuntimeError
from pylox.interpreter.interpreter import Interpreter, Return
from pylox.parser import Parser


class Lox:
    """
    Lox语言的主类
    
    包含运行Lox代码和处理错误的主要方法。
    """
    
    # 状态标志
    had_error = False
    had_runtime_error = False
    had_warnings = False
    
    # 解释器实例
    interpreter = None
    
    @classmethod
    def init(cls):
        """初始化Lox解释器"""
        if cls.interpreter is None:
            from pylox.interpreter.interpreter import Interpreter
            cls.interpreter = Interpreter()
    
    @classmethod
    def run_file(cls, path):
        """
        执行Lox脚本文件
        
        Args:
            path: str, 文件路径
        """
        try:
            # 重置状态
            cls.had_error = False
            cls.had_runtime_error = False
            
            # 初始化解释器
            cls.init()
            
            # 读取并执行文件
            with open(path, 'r', encoding='utf-8') as file:
                source = file.read()
                print(f"[执行文件] {path}")
                cls.run(source)
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{path}'", file=sys.stderr)
            sys.exit(65)  # EX_DATAERR
        except Exception as e:
            print(f"[异常] 执行 {path} 时发生异常: {e}")
            traceback.print_exc()
            sys.exit(70)  # EX_SOFTWARE
            
        # 语法错误时返回错误码
        if cls.had_error:
            sys.exit(65)  # EX_DATAERR
            
        # 运行时错误时返回错误码
        if cls.had_runtime_error:
            sys.exit(70)  # EX_SOFTWARE

    @classmethod
    def run_prompt(cls):
        """
        运行交互式REPL
        """
        try:
            # 初始化解释器
            cls.init()
            
            print("Lox 交互式模式 (Ctrl+D或Ctrl+Z退出)")
            # 开始REPL循环
            while True:
                print("> ", end="")
                line = input()
                if not line:
                    break
                cls.run(line, repl_mode=True)
                # 在REPL模式下，每次命令后重置错误状态
                cls.had_error = False
        except EOFError:
            print("\nGoodbye!")
        except KeyboardInterrupt:
            print("\nREPL被中断")
        except Exception as e:
            print(f"[异常]  REPL发生异常: {e}")
            traceback.print_exc()

    @classmethod
    def run(cls, source, repl_mode=False):
        """执行Lox代码

        Args:
            source: str, 源代码
            repl_mode: bool, 是否在REPL模式下运行

        Returns:
            解释执行的结果
        """
        
        # 确保解释器已初始化
        cls.init()
        
        # 扫描和解析
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        parser = Parser(tokens)
        statements = parser.parse()
        
        # 有语法错误时停止
        if cls.had_error:
            return None
        
        # 解析变量：确定变量引用绑定
        from pylox.resolver import Resolver
        resolver = Resolver(cls.interpreter)
        resolver.resolve(statements)
        
        # 有解析错误时停止
        if cls.had_error:
            return None
        
        # 在REPL模式下，如果只有一个表达式语句，则打印结果
        if repl_mode and len(statements) == 1:
            from pylox.syntax_tree.stmt import Expression
            if isinstance(statements[0], Expression):
                try:
                    # 对表达式求值并打印结果
                    result = cls.interpreter.evaluate(statements[0].expression)
                    print(cls.interpreter.stringify(result))
                    return result
                except Return as ret:
                    # 处理函数返回值异常
                    result = ret.value
                    print(cls.interpreter.stringify(result))
                    return result
        
        # 添加一个明确的包裹层来处理 Return 异常    
        try:
            # 将语句列表传递给解释器执行
            result = cls.interpreter.interpret(statements)
            return result
        except Return as ret:
            # 返回函数值
            return ret.value
        except Exception as e:
            # 处理其他异常
            print(f"[异常] 执行时发生异常: {e}")
            traceback.print_exc()
            return None

    @classmethod
    def error(cls, line, message):
        """
        报告行号的错误
        
        Args:
            line: int, 错误发生的行号
            message: str, 错误信息
        """
        cls.report(line, "", message)
        
    @classmethod
    def error_token(cls, token, message):
        """
        报告标记的错误
        
        Args:
            token: Token, 错误发生的标记
            message: str, 错误信息
        """
        if token.type == TokenType.EOF:
            cls.report(token.line, " at end", message)
        else:
            cls.report(token.line, f" at '{token.lexeme}'", message)
            
    @classmethod
    def runtime_error(cls, error):
        """
        报告运行时错误
        
        Args:
            error: RuntimeError, 运行时错误对象
        """
        message = f"[行 {error.token.line}] 运行时错误: {error}"
        print(message, file=sys.stderr)
        cls.had_runtime_error = True

    @classmethod
    def report(cls, line, where, message):
        """
        输出错误信息
        
        Args:
            line: int, 错误发生的行号
            where: str, 错误位置的额外信息
            message: str, 错误信息
        """
        message = f"[行 {line}] 错误{where}: {message}"
        print(message, file=sys.stderr)
        cls.had_error = True
        
    @classmethod
    def evaluate(cls, source):
        """
        计算单个表达式的值（便捷方法）
        
        Args:
            source: str, 源代码表达式
            
        Returns:
            表达式的值，如果有错误则返回None
        """
        cls.had_error = False
        cls.had_runtime_error = False
        
        # 扫描：源代码 -> 词法标记
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        # 有词法错误时停止
        if cls.had_error:
            return None
            
        # 解析：词法标记 -> 语句列表
        from pylox.parser import Parser
        
        parser = Parser(tokens)
        
        # 尝试解析为表达式
        try:
            expression = parser.parse_expression()
            
            # 有语法错误时停止
            if cls.had_error:
                return None
            
            # 如果解析成功，获取表达式的值并返回
            if expression:
                return cls.interpreter.evaluate(expression)
                
        except Exception:
            # 如果解析为表达式失败，尝试解析为语句列表
            statements = parser.parse()
            
            # 有语法错误时停止
            if cls.had_error:
                return None
                
            # 解释执行
            try:
                return cls.run(source)
            except Return as ret:
                return ret.value
                
        return None

    @classmethod
    def warning(cls, message):
        """
        输出警告信息
        
        与错误不同，警告不会停止程序执行，但会提醒用户潜在问题。
        
        Args:
            message: str, 警告信息
        """
        print(f"[警告] {message}", file=sys.stderr)
        cls.had_warnings = True


if __name__ == "__main__":
    """
    当脚本直接运行时执行的入口点
    
    如果提供一个参数，将其作为文件路径执行
    否则启动交互式解释器
    """
    print("Lox Python解释器")
    if len(sys.argv) > 2:
        print("用法: python pylox/lox.py [脚本文件]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        Lox.run_file(sys.argv[1])
    else:
        Lox.run_prompt()