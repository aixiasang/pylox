#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试控制流功能
"""

import unittest
import io
import sys
from pylox.lox import Lox


class TestControlFlow(unittest.TestCase):
    """测试控制流功能"""
    
    def setUp(self):
        """测试前准备"""
        # 重置错误状态
        Lox.had_error = False
        Lox.had_runtime_error = False
        
        # 捕获标准输出
        self.stdout_backup = sys.stdout
        self.captured_output = io.StringIO()
        sys.stdout = self.captured_output
    
    def tearDown(self):
        """测试后清理"""
        # 恢复标准输出
        sys.stdout = self.stdout_backup
    
    def test_if_statement(self):
        """测试if语句"""
        code = """
        var a = 10;
        if (a > 5) {
            print "a > 5";
        } else {
            print "a <= 5";
        }
        
        if (a < 5) {
            print "a < 5";
        } else {
            print "a >= 5";
        }
        """
        
        Lox.run(code)
        output = self.captured_output.getvalue().strip().split('\n')
        
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "a > 5")
        self.assertEqual(output[1], "a >= 5")
        
    def test_logical_operators(self):
        """测试逻辑运算符"""
        code = """
        print true and true;
        print true and false;
        print false and true;
        print false and false;
        
        print true or true;
        print true or false;
        print false or true;
        print false or false;
        
        // 测试短路求值
        var a = "not changed";
        false and (a = "changed");
        print a; // 应该是 "not changed"
        
        a = "not changed";
        true or (a = "changed");
        print a; // 应该是 "not changed"
        """
        
        Lox.run(code)
        output = self.captured_output.getvalue().strip().split('\n')
        
        self.assertEqual(len(output), 10)
        self.assertEqual(output[0], "true")
        self.assertEqual(output[1], "false")
        self.assertEqual(output[2], "false")
        self.assertEqual(output[3], "false")
        self.assertEqual(output[4], "true")
        self.assertEqual(output[5], "true")
        self.assertEqual(output[6], "true")
        self.assertEqual(output[7], "false")
        self.assertEqual(output[8], "not changed")
        self.assertEqual(output[9], "not changed")
        
    def test_while_loop(self):
        """测试while循环"""
        code = """
        var i = 0;
        var sum = 0;
        while (i < 5) {
            sum = sum + i;
            i = i + 1;
        }
        print sum;
        """
        
        Lox.run(code)
        output = self.captured_output.getvalue().strip()
        
        self.assertEqual(output, "10")
        
    def test_for_loop(self):
        """测试for循环"""
        code = """
        var sum = 0;
        for (var i = 0; i < 5; i = i + 1) {
            sum = sum + i;
        }
        print sum;
        
        // 测试for循环的不同部分
        // 省略初始化部分
        sum = 0;
        var i = 0;
        for (; i < 5; i = i + 1) {
            sum = sum + i;
        }
        print sum;
        """
        
        Lox.run(code)
        output = self.captured_output.getvalue().strip().split('\n')
        
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "10")
        self.assertEqual(output[1], "10")


if __name__ == "__main__":
    unittest.main() 