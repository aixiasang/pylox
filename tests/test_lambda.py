#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Lambda表达式功能
"""

import unittest
from pylox.scanner import Scanner, TokenType
from pylox.parser import Parser
from pylox.lox import Lox
from pylox.syntax_tree import Lambda, Block, Literal, Variable, Binary
from pylox.syntax_tree.ast_printer import AstPrinter
from pylox.scanner.token import Token
from pylox.interpreter import Interpreter


class TestLambda(unittest.TestCase):
    """测试Lambda表达式功能"""
    
    def setUp(self):
        """测试前设置"""
        Lox.had_error = False
        Lox.had_runtime_error = False
        self.interpreter = Interpreter()
    
    def parse_expression(self, source):
        """
        解析表达式
        
        Args:
            source: str, 源代码
            
        Returns:
            Expr: 表达式对象
        """
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        return parser.parse_expression()
    
    def parse_program(self, source):
        """
        解析完整程序
        
        Args:
            source: str, 源代码
            
        Returns:
            list[Stmt]: 语句列表
        """
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        return parser.parse()
    
    def test_lambda_creation(self):
        """测试Lambda表达式创建"""
        # 创建一个Lambda表达式
        params = [Token(TokenType.IDENTIFIER, "x", None, 1)]
        body = [Literal(42)]
        lambda_expr = Lambda(params, body)
        
        # 打印测试
        printer = AstPrinter()
        self.assertEqual(printer.print(lambda_expr), "(lambda x)")
        
    def test_lambda_parsing(self):
        """测试Lambda表达式解析"""
        expr = self.parse_expression("fun (x) { return x * x; }")
        self.assertIsInstance(expr, Lambda)
        self.assertEqual(len(expr.params), 1)
        self.assertEqual(expr.params[0].lexeme, "x")
    
    def test_lambda_as_variable(self):
        """测试Lambda表达式作为变量值"""
        program = self.parse_program("var square = fun (x) { return x * x; }; print square(5);")
        self.interpreter.interpret(program)
        # 结果在stdout
        
    def test_lambda_immediate_call(self):
        """测试Lambda表达式立即调用"""
        program = self.parse_program("print fun (x) { return x * x; }(5);")
        self.interpreter.interpret(program)
        # 结果在stdout
        
    def test_lambda_closure(self):
        """测试Lambda表达式闭包功能"""
        program = self.parse_program("""
var makeAdder = fun (n) {
  return fun (x) {
    return x + n;
  };
};
var add5 = makeAdder(5);
print add5(10);
        """)
        self.interpreter.interpret(program)
        # 结果在stdout
        
    def test_lambda_as_argument(self):
        """测试Lambda表达式作为参数"""
        program = self.parse_program("""
fun apply(func, x, y) {
  return func(x, y);
}
print apply(fun (a, b) { return a * b; }, 4, 5);
        """)
        self.interpreter.interpret(program)
        # 结果在stdout
        
    def test_parameter_scope(self):
        """测试参数与局部变量的作用域"""
        program = self.parse_program("""
fun scope(a) {
  print "参数a: " + a;
  var a = "local";
  print "局部变量a: " + a;
}
scope("parameter");
        """)
        self.interpreter.interpret(program)
        # 结果在stdout


if __name__ == "__main__":
    unittest.main()