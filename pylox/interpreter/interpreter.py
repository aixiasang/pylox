#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
解释器实现

遍历语法树并执行代码
"""

from pylox.syntax_tree.visitor import Visitor
from pylox.scanner.token_type import TokenType
from pylox.interpreter.runtime_error import RuntimeError
from pylox.interpreter.environment import Environment
from pylox.interpreter.lox_callable import LoxFunction
from pylox.interpreter.lox_class import LoxClass, LoxInstance


class Interpreter(Visitor):
    """
    解释器类
    
    遍历AST并执行代码，实现Visitor模式
    """
    
    def __init__(self):
        """初始化解释器"""
        self.globals = Environment()  # 全局环境
        self.environment = self.globals  # 当前环境，初始为全局环境
        from pylox.lox import Lox
        self.lox = Lox  # Lox类，用于错误报告
        self.locals = {}  # 局部变量表，存储表达式到作用域深度的映射
        
        # 初始化全局函数
        from pylox.interpreter.natives.clock import Clock
        self.globals.define("clock", Clock())
    
    def interpret(self, statements):
        """
        解释执行语句列表
        
        Args:
            statements: list[Stmt], 语句列表
        """
        last_result = None
        try:
            for statement in statements:
                try:
                    last_result = self.execute(statement)
                except Return as ret:
                    # 捕获每个语句可能引发的Return异常
                    # 如果是函数内部的return应该在call方法中处理
                    # 但这里作为安全措施捕获可能的漏网之鱼
                    last_result = ret.value
            return last_result
        except RuntimeError as error:
            self.lox.runtime_error(error)
            return None
    
    def execute(self, stmt):
        """
        执行语句
        
        Args:
            stmt: Stmt, 语句对象
            
        Returns:
            Any, 执行结果
        """
        return stmt.accept(self)
    
    def resolve(self, expr, depth):
        """
        解析表达式的作用域深度
        
        Args:
            expr: Expr, 表达式对象
            depth: int, 作用域深度
        """
        self.locals[expr] = depth
    
    def evaluate(self, expr):
        """
        计算表达式的值
        
        Args:
            expr: Expr, 表达式对象
            
        Returns:
            Any, 表达式的值
        """
        return expr.accept(self)
    
    def execute_block(self, statements, environment):
        """
        执行代码块
        
        在指定的环境中执行一系列语句，执行完毕后恢复原环境
        
        Args:
            statements: list[Stmt], 语句列表
            environment: Environment, 执行环境
        """
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def stringify(self, value):
        """
        将值转换为字符串
        
        Args:
            value: Any, 需要转换的值
            
        Returns:
            str, 转换后的字符串
        """
        if value is None:
            return "nil"
        
        if isinstance(value, bool):
            return str(value).lower()
        
        if isinstance(value, (int, float)):
            text = str(value)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        
        return str(value)
    
    # 访问语句方法
    def visit_expression_stmt(self, stmt):
        """访问表达式语句"""
        self.evaluate(stmt.expression)
        return None
    
    def visit_print_stmt(self, stmt):
        """访问print语句"""
        from pylox.lox import Lox
        
        value = self.evaluate(stmt.expression)
        
        if Lox.debug_mode:
            print(f"[调试] 打印值: {self.stringify(value)}")
            
        print(self.stringify(value))
        return None
    
    def visit_var_stmt(self, stmt):
        """访问变量声明语句"""
        value = None
        if stmt.initializer is not None:
            try:
                value = self.evaluate(stmt.initializer)
            except RuntimeError as e:
                # 如果是因为变量未初始化引起的错误，尝试从外部环境获取同名变量
                if hasattr(e, 'token') and e.token.lexeme == stmt.name.lexeme:
                    try:
                        # 尝试从外部环境获取同名变量
                        enclosing = self.environment.enclosing
                        if enclosing:
                            value = enclosing.get(stmt.name)
                    except:
                        # 如果外部环境也没有，保持原错误
                        raise e
                else:
                    # 其他运行时错误，直接抛出
                    raise
                
        # 确保value不为None后再定义
        if value is None:
            value = None  # 显式设置为None，而不是使用变量本身
            
        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def visit_block_stmt(self, stmt):
        """访问块语句"""
        # 创建新环境并执行块中的语句
        self.execute_block(stmt.statements, Environment(self.environment))
        return None
    
    def visit_if_stmt(self, stmt):
        """访问if语句"""
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None
    
    def visit_while_stmt(self, stmt):
        """访问while语句"""
        while self.is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except BreakException:
                break
        return None
    
    def visit_break_stmt(self, stmt):
        """访问break语句"""
        raise BreakException()
    
    def visit_function_stmt(self, stmt):
        """访问函数声明语句"""
        # 创建函数对象，捕获当前环境
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)
        return None
    
    def visit_return_stmt(self, stmt):
        """访问return语句"""
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        
        # 使用异常传递返回值
        raise Return(value)
    
    def visit_class_stmt(self, stmt):
        """访问类声明语句"""
        # 处理超类
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise RuntimeError(stmt.superclass.name, "超类必须是一个类。")
        
        # 在当前环境中定义类名
        self.environment.define(stmt.name.lexeme, None)
        
        # 处理super关键字
        if stmt.superclass is not None:
            # 创建新环境存储super引用
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        
        # 处理类方法
        methods = {}
        for method in stmt.methods:
            # 创建函数对象，标记是否为初始化方法、getter方法或静态方法
            is_initializer = method.name.lexeme == "init"
            is_getter = method.is_getter
            is_static = method.is_static
            
            function = LoxFunction(method, self.environment, 
                                   is_initializer, is_getter, is_static)
            methods[method.name.lexeme] = function
        
        # 创建类对象
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        
        # 如果有超类，弹出super环境
        if stmt.superclass is not None:
            self.environment = self.environment.enclosing
            
        # 更新类定义
        self.environment.assign(stmt.name, klass)
        return None
    
    # 访问表达式方法
    def visit_literal_expr(self, expr):
        """访问字面量表达式"""
        return expr.value
    
    def visit_grouping_expr(self, expr):
        """访问分组表达式"""
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr):
        """访问一元表达式"""
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
            
        # 不应该到达这里
        return None
    
    def visit_binary_expr(self, expr):
        """访问二元表达式"""
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == TokenType.PLUS:
            # 字符串拼接
            if isinstance(left, str) or isinstance(right, str):
                # 将数字转为字符串时，如果是整数，去掉小数点
                if isinstance(left, float) and left.is_integer():
                    left = int(left)
                if isinstance(right, float) and right.is_integer():
                    right = int(right)
                return str(left) + str(right)
            # 数字相加
            return float(left) + float(right)
        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            # 检查除以零
            if right == 0:
                raise RuntimeError(expr.operator, "除数不能为零。")
            return float(left) / float(right)
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return float(left) * float(right)
        
        # 不应该到达这里
        return None
    
    def visit_call_expr(self, expr):
        """访问函数调用表达式"""
        callee = self.evaluate(expr.callee)
        
        # 计算参数值
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        # 检查是否是可调用对象
        if not hasattr(callee, 'call'):
            raise RuntimeError(expr.paren, "只能调用函数和类。")
        
        # 检查参数数量
        if len(arguments) != callee.arity():
            raise RuntimeError(expr.paren, 
                              f"需要{callee.arity()}个参数但得到{len(arguments)}个。")
        
        # 调用函数，并捕获可能的Return异常
        try:
            return callee.call(self, arguments)
        except Return as ret:
            # 函数调用中产生的Return异常在这里被捕获，并返回其值
            return ret.value
    
    def visit_get_expr(self, expr):
        """访问属性访问表达式"""
        # 计算对象表达式
        obj = self.evaluate(expr.object)
        
        # 检查是否为类（静态方法调用）
        from pylox.interpreter.lox_class import LoxClass
        if isinstance(obj, LoxClass):
            # 查找静态方法
            method = obj.find_static_method(expr.name.lexeme)
            if method is not None:
                return method
            
            # 如果找不到静态方法，抛出错误
            raise RuntimeError(expr.name, f"未定义的静态方法 '{expr.name.lexeme}'。")
        
        # 确保对象是一个实例
        from pylox.interpreter.lox_class import LoxInstance
        if isinstance(obj, LoxInstance):
            # 获取属性或方法
            return obj.get(expr.name, self)
        
        # 如果不是实例或类，抛出运行时错误
        raise RuntimeError(expr.name, "只能从实例或类上获取属性。")
    
    def visit_set_expr(self, expr):
        """访问属性设置表达式"""
        obj = self.evaluate(expr.object)
        
        # 确保对象是实例
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name, "只能在实例上设置属性。")
        
        # 计算值并设置属性
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value
    
    def visit_this_expr(self, expr):
        """访问this表达式"""
        return self.look_up_variable(expr.keyword, expr)
    
    def visit_super_expr(self, expr):
        """访问super表达式"""
        from pylox.lox import Lox
        
        if Lox.debug_mode:
            print(f"[调试] 处理super表达式: {expr.method.lexeme}")
        
        # 获取super在环境中的深度
        distance = self.locals.get(expr)
        
        if Lox.debug_mode:
            print(f"[调试] super作用域深度: {distance}")
        
        # 获取超类
        superclass = self.environment.get_at(distance, "super")
        
        if Lox.debug_mode:
            print(f"[调试] 获取到超类: {superclass}")
        
        # 获取this实例（子类实例）
        instance = self.environment.get_at(distance - 1, "this")
        
        if Lox.debug_mode:
            print(f"[调试] 获取到实例: {instance}")
        
        # 在超类中查找方法
        method = superclass.find_method(expr.method.lexeme)
        
        if Lox.debug_mode:
            print(f"[调试] 在超类中查找方法: {expr.method.lexeme}, 结果: {method}")
        
        if method is None:
            raise RuntimeError(expr.method, f"未定义的属性'{expr.method.lexeme}'。")
        
        # 将方法绑定到子类实例
        return method.bind(instance)
    
    def visit_variable_expr(self, expr):
        """访问变量表达式"""
        return self.look_up_variable(expr.name, expr)
    
    def look_up_variable(self, name, expr):
        """
        查找变量的值
        
        根据解析器提供的作用域深度信息查找变量值
        
        Args:
            name: Token, 变量名标记
            expr: Expr, 表达式对象
            
        Returns:
            Any, 变量值
        """
        distance = self.locals.get(expr)
        if distance is not None:
            # 局部变量，从指定深度的环境中获取
            return self.environment.get_at(distance, name.lexeme)
        else:
            # 全局变量，从全局环境中获取
            return self.globals.get(name)
    
    def visit_assign_expr(self, expr):
        """访问赋值表达式"""
        # 计算右侧表达式的值
        value = self.evaluate(expr.value)
        
        # 根据变量作用域深度进行赋值
        distance = self.locals.get(expr)
        if distance is not None:
            # 局部变量
            self.environment.assign_at(distance, expr.name, value)
        else:
            # 全局变量
            self.globals.assign(expr.name, value)
        
        return value
    
    def visit_logical_expr(self, expr):
        """访问逻辑表达式"""
        left = self.evaluate(expr.left)
        
        # 短路求值
        if expr.operator.type == TokenType.OR:
            # 对于OR，如果左侧为真，则直接返回左侧值
            if self.is_truthy(left):
                return left
        else:
            # 对于AND，如果左侧为假，则直接返回左侧值
            if not self.is_truthy(left):
                return left
        
        # 不能短路，计算右侧表达式
        return self.evaluate(expr.right)
    
    def visit_lambda_expr(self, expr):
        """访问Lambda表达式"""
        # 创建匿名函数，捕获当前环境
        return LoxFunction(expr, self.environment, False)
    
    def is_truthy(self, value):
        """
        判断值是否为"真"
        
        Lox中的真值规则：
        - None和False为假
        - 其他值都为真
        
        Args:
            value: Any, 需要判断的值
            
        Returns:
            bool, 值是否为"真"
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True
    
    def is_equal(self, a, b):
        """
        判断两个值是否相等
        
        Args:
            a: Any, 第一个值
            b: Any, 第二个值
            
        Returns:
            bool, 两个值是否相等
        """
        # None只等于None
        if a is None and b is None:
            return True
        if a is None:
            return False
        
        # 使用Python的相等性判断
        return a == b
    
    def check_number_operand(self, operator, operand):
        """
        检查操作数是否为数字
        
        Args:
            operator: Token, 运算符标记
            operand: Any, 操作数
            
        Raises:
            RuntimeError: 操作数不是数字
        """
        if isinstance(operand, (int, float)):
            return
        raise RuntimeError(operator, "操作数必须是数字。")
    
    def check_number_operands(self, operator, left, right):
        """
        检查两个操作数是否都为数字
        
        Args:
            operator: Token, 运算符标记
            left: Any, 左操作数
            right: Any, 右操作数
            
        Raises:
            RuntimeError: 操作数不是数字
        """
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError(operator, "操作数必须是数字。")


class BreakException(Exception):
    """
    中断异常类
    
    用于实现break语句跳出循环
    """
    pass


class Return(Exception):
    """
    返回值异常类
    
    用于从函数中返回值
    """
    
    def __init__(self, value):
        """
        初始化返回值异常
        
        Args:
            value: Any, 返回值
        """
        super().__init__()
        self.value = value