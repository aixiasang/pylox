#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
解析器模块

提供变量解析和绑定的功能，以解决词法作用域问题。
"""

from pylox.resolver.resolver import Resolver, FunctionType

__all__ = ['Resolver', 'FunctionType']