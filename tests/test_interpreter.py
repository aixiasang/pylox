#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试解释器功能
"""

import unittest
import io
import sys
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    """测试解释器功能"""
    
    def setUp(self):
        """测试前准备"""
        # 重置错误状态
        from pylox.lox import Lox
        Lox.had_error = False
        Lox.had_runtime_error = False
        
        # 创建解释器
        self.interpreter = Interpreter()
    
    def interpret(self, source):
        """
        解释执行源代码
        
        Args:
            source: str, 源代码
            
        Returns:
            解释执行的结果
        """
        from pylox.lox import Lox
        
        # 确保解释器已初始化
        if Lox.interpreter is None:
            from pylox.interpreter import Interpreter
            Lox.interpreter = Interpreter()
            
        # 使用Lox类的evaluate方法计算表达式
        return Lox.evaluate(source)
    
    def test_literal_values(self):
        """测试字面量值"""
        # 数字
        self.assertEqual(self.interpret("123"), 123.0)
        self.assertEqual(self.interpret("-123"), -123.0)
        
        # 字符串
        self.assertEqual(self.interpret("\"hello\""), "hello")
        
        # 布尔值
        self.assertEqual(self.interpret("true"), True)
        self.assertEqual(self.interpret("false"), False)
        
        # Nil
        self.assertIsNone(self.interpret("nil"))
    
    def test_arithmetic(self):
        """测试算术运算"""
        # 加法
        self.assertEqual(self.interpret("1 + 2"), 3.0)
        
        # 减法
        self.assertEqual(self.interpret("5 - 3"), 2.0)
        
        # 乘法
        self.assertEqual(self.interpret("2 * 3"), 6.0)
        
        # 除法
        self.assertEqual(self.interpret("8 / 2"), 4.0)
        
        # 复合运算
        self.assertEqual(self.interpret("2 + 3 * 4"), 14.0)
        self.assertEqual(self.interpret("(2 + 3) * 4"), 20.0)
        self.assertEqual(self.interpret("2 + 3 * 4 - 6 / 2"), 11.0)
        
        # 一元操作符
        self.assertEqual(self.interpret("-5"), -5.0)
        self.assertEqual(self.interpret("-(2 + 3)"), -5.0)
    
    def test_comparison(self):
        """测试比较运算"""
        # 大于
        self.assertEqual(self.interpret("5 > 3"), True)
        self.assertEqual(self.interpret("3 > 5"), False)
        
        # 大于等于
        self.assertEqual(self.interpret("5 >= 5"), True)
        self.assertEqual(self.interpret("4 >= 5"), False)
        
        # 小于
        self.assertEqual(self.interpret("3 < 5"), True)
        self.assertEqual(self.interpret("5 < 3"), False)
        
        # 小于等于
        self.assertEqual(self.interpret("5 <= 5"), True)
        self.assertEqual(self.interpret("5 <= 4"), False)
    
    def test_equality(self):
        """测试相等性运算"""
        # 相等
        self.assertEqual(self.interpret("5 == 5"), True)
        self.assertEqual(self.interpret("5 == 6"), False)
        self.assertEqual(self.interpret("\"hello\" == \"hello\""), True)
        self.assertEqual(self.interpret("\"hello\" == \"world\""), False)
        self.assertEqual(self.interpret("true == true"), True)
        self.assertEqual(self.interpret("false == true"), False)
        self.assertEqual(self.interpret("nil == nil"), True)
        
        # 不等
        self.assertEqual(self.interpret("5 != 6"), True)
        self.assertEqual(self.interpret("5 != 5"), False)
        self.assertEqual(self.interpret("\"hello\" != \"world\""), True)
        self.assertEqual(self.interpret("\"hello\" != \"hello\""), False)
        self.assertEqual(self.interpret("true != false"), True)
        self.assertEqual(self.interpret("true != true"), False)
        self.assertEqual(self.interpret("nil != 5"), True)
    
    def test_logical_operators(self):
        """测试逻辑运算符"""
        # 逻辑非
        self.assertEqual(self.interpret("!true"), False)
        self.assertEqual(self.interpret("!false"), True)
        self.assertEqual(self.interpret("!!true"), True)
        self.assertEqual(self.interpret("!nil"), True)
        self.assertEqual(self.interpret("!0"), False)
    
    def test_string_operations(self):
        """测试字符串操作"""
        # 字符串连接
        self.assertEqual(self.interpret("\"hello\" + \" \" + \"world\""), "hello world")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 捕获标准错误输出
        stderr_backup = sys.stderr
        sys.stderr = io.StringIO()

        try:
            # 类型错误：对非数字取负
            # 对于错误测试，我们不添加分号，而是直接测试解释器的行为
            scanner = Scanner("-\"hello\"")
            tokens = scanner.scan_tokens()
            parser = Parser(tokens)
            expression = parser.parse_expression()

            # 确保解析成功
            self.assertIsNotNone(expression)

            # 创建一个表达式语句
            from pylox.syntax_tree.stmt import Expression
            statement = Expression(expression)

            # 解释执行，应该捕获运行时错误
            result = self.interpreter.interpret([statement])
            self.assertIsNone(result)

            from pylox.lox import Lox
            self.assertTrue(Lox.had_runtime_error)

            # 重置错误状态
            Lox.had_runtime_error = False

            # 测试字符串连接 - 使用Lox.evaluate而不是直接调用interpreter
            str_result = Lox.evaluate("5 + \"hello\"")
            self.assertEqual(str_result, "5hello")

        finally:
            # 恢复标准错误输出
            sys.stderr = stderr_backup


if __name__ == "__main__":
    unittest.main()
