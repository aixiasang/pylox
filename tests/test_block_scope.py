#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试块级作用域变量行为
"""

import unittest
import io
import sys
from pylox.lox import Lox


class TestBlockScope(unittest.TestCase):
    """测试块级作用域特性"""
    
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
    
    def test_block_var_initialization(self):
        """测试块内变量初始化"""
        # 使用外部变量的值初始化块内变量
        code = """
        var a = 1;
        var outer_a = a; // 保存外部a的值
        {
          var a = outer_a + 2; // 使用外部a的值
          print a;
        }
        print a;
        """
        
        Lox.run(code)
        output = self.captured_output.getvalue().strip().split('\n')
        
        # 块内的a应该是3，块外的a仍然是1
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "3")
        self.assertEqual(output[1], "1")
        
        # 确认没有错误发生
        self.assertFalse(Lox.had_error)
        self.assertFalse(Lox.had_runtime_error)
    
    def test_uninitialized_var_access(self):
        """测试访问未初始化变量"""
        # 声明但不初始化变量b，然后尝试访问它
        code = """
        var a = 1;
        var b;
        print a;
        print b;
        """
        
        Lox.run(code)
        
        # 现在访问未初始化变量应该抛出运行时错误
        self.assertTrue(Lox.had_runtime_error)


if __name__ == "__main__":
    unittest.main() 