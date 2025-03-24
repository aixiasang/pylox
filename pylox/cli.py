#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyLox CLI模块

提供命令行接口来运行Lox解释器
"""

import sys
from pylox.lox import Lox


def main():
    """
    命令行入口函数
    
    处理命令行参数，根据参数启动解释器的不同模式。
    可以运行交互式REPL或执行Lox脚本文件。
    """
    args = sys.argv[1:]
    if len(args) > 1:
        print("Usage: pylox [script]")
        sys.exit(64)
    elif len(args) == 1:
        Lox.run_file(args[0])
    else:
        Lox.run_prompt()


if __name__ == "__main__":
    main() 