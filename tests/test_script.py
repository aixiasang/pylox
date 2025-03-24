#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试脚本，用于验证块作用域中引用外部同名变量的行为"""

import io
import sys
from pylox.lox import Lox

def test_block_var_initialization():
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
    
    # 捕获标准输出
    stdout_backup = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output
    
    try:
        # 重置错误状态
        Lox.had_error = False
        Lox.had_runtime_error = False
        
        # 运行代码
        Lox.run(code)
        
        output = captured_output.getvalue().strip().split('\n')
        
        # 块内的a应该是3，块外的a仍然是1
        assert len(output) == 2
        assert output[0] == "3"
        assert output[1] == "1"
        
        # 确认没有错误发生
        assert not Lox.had_error
        assert not Lox.had_runtime_error
    finally:
        # 恢复标准输出
        sys.stdout = stdout_backup

if __name__ == "__main__":
    test_block_var_initialization()
    print("测试通过!")