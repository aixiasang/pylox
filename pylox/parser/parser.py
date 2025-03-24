#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
递归下降解析器

将标记序列解析为抽象语法树，实现了Lox语言的表达式语法。
使用递归下降解析技术处理不同优先级的表达式。
"""

from pylox.scanner.token_type import TokenType
from pylox.syntax_tree import Binary, Grouping, Literal, Unary, Variable, Assign, Logical, Call, Lambda, Super
from pylox.syntax_tree import Get, Set, This  # 添加新的表达式类型
from pylox.syntax_tree import Expression, Print, Var, Block, If, While, Break, Function, Return, Class  # 添加Class


class ParseError(Exception):
    """解析错误异常"""
    pass


class Parser:
    """
    递归下降解析器
    
    实现了Lox语言的表达式语法解析，采用递归下降解析算法。
    """
    
    def __init__(self, tokens):
        """
        初始化解析器
        
        Args:
            tokens: List[Token], 标记列表
        """
        self.tokens = tokens  # 要解析的标记列表
        self.current = 0      # 当前标记位置
    
    def parse(self):
        """
        解析标记序列，构建AST
        
        Returns:
            list[Stmt], 语句列表
        """
        statements = []
        
        while not self.is_at_end():
            statements.append(self.declaration())
            
        return statements
        
    def parse_expression(self):
        """
        解析单个表达式
        
        Returns:
            Expr: 解析得到的表达式对象，解析失败则返回None
        """
        try:
            return self.expression()
        except ParseError:
            return None
    
    def declaration(self):
        """
        解析声明语句
        
        声明 → classDecl | funDecl | varDecl | statement
        
        Returns:
            Stmt: 声明语句
        """
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUN):
                return self.function_declaration("function")
            if self.match(TokenType.VAR):
                return self.var_declaration()
                
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
            
    def function_declaration(self, kind, is_static=False, is_getter=False):
        """
        解析函数声明
        
        语法规则：
        funDecl → "fun" function ;
        function → IDENTIFIER "(" parameters? ")" block ;
        method → IDENTIFIER "(" parameters? ")" block 
               | IDENTIFIER block ;  // getter方法，没有参数
        
        Args:
            kind: str, 函数类型，用于错误消息
            is_static: bool, 是否是静态方法
            is_getter: bool, 是否是getter方法
            
        Returns:
            Function: 函数声明对象
            
        Raises:
            ParseError: 解析错误时抛出
        """
        name = self.consume(TokenType.IDENTIFIER, "期望" + kind + "名称。")
        
        # 检查是否是getter方法（方法名后直接跟左大括号，没有参数列表）
        if self.check(TokenType.LEFT_BRACE):
            is_getter = True
            parameters = []  # getter没有参数
        else:
            # 普通方法或静态方法需要参数列表
            self.consume(TokenType.LEFT_PAREN, "期望" + kind + "名后的'('。")
            
            parameters = []
            if not self.check(TokenType.RIGHT_PAREN):
                while True:
                    if len(parameters) >= 255:
                        self.error(self.peek(), "函数参数不能超过255个。")
                        
                    parameters.append(
                        self.consume(TokenType.IDENTIFIER, "期望参数名。")
                    )
                    
                    if not self.match(TokenType.COMMA):
                        break
            
            self.consume(TokenType.RIGHT_PAREN, "期望')'。")
        
        # 解析函数体
        self.consume(TokenType.LEFT_BRACE, "期望" + kind + "体开始的'{'。")
        body = self.block()
        
        return Function(name, parameters, body, is_static, is_getter)
            
    def var_declaration(self):
        """
        解析变量声明
        
        varDecl → "var" IDENTIFIER ( "=" expression )? ";" ;
        
        Returns:
            Var: 变量声明语句
        """
        name = self.consume(TokenType.IDENTIFIER, "期望变量名。")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            # 如果有初始化表达式，则解析它
            
            # 检查是否在尝试使用变量自身作为初始化器
            # 因为我们现在支持内部作用域变量引用外部同名变量，所以需要特殊处理
            # 这部分逻辑需要在resolver中处理，这里只解析语法
            initializer = self.expression()
            
        self.consume(TokenType.SEMICOLON, "期望 ';' 在变量声明后。")
        return Var(name, initializer)
    
    def statement(self):
        """
        解析语句
        
        语法规则：
        statement → exprStmt
                  | printStmt
                  | block
                  | ifStmt
                  | whileStmt
                  | forStmt
                  | breakStmt
                  | returnStmt ;
        
        Returns:
            Stmt: 语句对象
            
        Raises:
            ParseError: 解析错误
        """
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.BREAK):
            return self.break_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
            
        return self.expression_statement()
    
    def print_statement(self):
        """
        printStmt → "print" expression ";"
        
        解析打印语句
        
        Returns:
            Print: 打印语句对象
            
        Raises:
            ParseError: 打印语句格式错误时抛出
        """
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "打印语句后需要';'。")
        return Print(value)
    
    def block(self):
        """
        block → "{" declaration* "}"
        
        解析代码块
        
        Returns:
            List[Stmt]: 代码块中的语句列表
            
        Raises:
            ParseError: 代码块格式错误时抛出
        """
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
            
        self.consume(TokenType.RIGHT_BRACE, "代码块后需要'}'。")
        return statements
    
    def expression_statement(self):
        """
        exprStmt → expression ";"
        
        解析表达式语句
        
        Returns:
            Expression: 表达式语句对象
            
        Raises:
            ParseError: 表达式语句格式错误时抛出
        """
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "表达式后需要';'。")
        return Expression(expr)
    
    def if_statement(self):
        """
        解析if语句
        
        格式：if ( 条件 ) 语句 [else 语句]
        
        Returns:
            If: 条件语句对象
            
        Raises:
            ParseError: 解析出错时抛出
        """
        self.consume(TokenType.LEFT_PAREN, "if语句后需要'('。")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "条件表达式后需要')'。")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
            
        return If(condition, then_branch, else_branch)
    
    def while_statement(self):
        """
        解析while语句
        
        格式：while ( 条件 ) 语句
        
        Returns:
            While: 循环语句对象
            
        Raises:
            ParseError: 解析出错时抛出
        """
        self.consume(TokenType.LEFT_PAREN, "while语句后需要'('。")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "条件表达式后需要')'。")
        
        body = self.statement()
        
        return While(condition, body)
    
    def for_statement(self):
        """
        解析for语句
        
        格式：for ( 初始化; 条件; 递增 ) 语句
        
        for语句会被转换为等价的while循环
        
        Returns:
            Stmt: 语句对象
            
        Raises:
            ParseError: 解析出错时抛出
        """
        self.consume(TokenType.LEFT_PAREN, "for语句后需要'('。")
        
        # 初始化部分
        initializer = None
        if self.match(TokenType.SEMICOLON):
            # 没有初始化部分
            pass
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
            
        # 条件部分
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "循环条件后需要';'。")
        
        # 递增部分
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "for循环声明后需要')'。")
        
        # 循环体
        body = self.statement()
        
        # 重写为while循环
        # 添加递增部分到循环体末尾
        if increment is not None:
            body = Block([body, Expression(increment)])
            
        # 如果条件为空，使用true作为条件
        if condition is None:
            condition = Literal(True)
            
        # 转换为while循环
        body = While(condition, body)
        
        # 如果有初始化器，将其添加在循环之前
        if initializer is not None:
            body = Block([initializer, body])
            
        return body
    
    def break_statement(self):
        """
        解析break语句
        
        语法规则：
        breakStmt → "break" ";" ;
        
        Returns:
            Break: break语句对象
            
        Raises:
            ParseError: 解析错误
        """
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "break语句后需要';'。")
        return Break(keyword)
    
    def return_statement(self):
        """
        解析return语句
        
        语法规则：
        returnStmt → "return" expression? ";" ;
        
        Returns:
            Return: return语句对象
            
        Raises:
            ParseError: 解析错误时抛出
        """
        keyword = self.previous()
        
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
            
        self.consume(TokenType.SEMICOLON, "return语句后需要';'。")
        return Return(keyword, value)
    
    def expression(self):
        """
        解析表达式
        
        grammar: assignment
        
        Returns:
            Expr: 表达式对象
        """
        return self.assignment()
    
    def assignment(self):
        """
        解析赋值表达式
        
        assignment → IDENTIFIER "=" assignment
                   | logic_or
        
        Returns:
            Expr: 赋值表达式或逻辑或表达式
        """
        expr = self.or_expression()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                get = expr
                return Set(get.object, get.name, value)
                
            self.error(equals, "无效的赋值目标。")
            
        return expr
    
    def or_expression(self):
        """
        解析逻辑or表达式
        
        grammar: and_expr ( "or" and_expr )*
        
        Returns:
            Expr: 逻辑表达式对象
        """
        expr = self.and_expr()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr, operator, right)
            
        return expr
    
    def and_expr(self):
        """
        解析逻辑and表达式
        
        grammar: equality ( "and" equality )*
        
        Returns:
            Expr: 逻辑表达式对象
        """
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
            
        return expr
    
    def equality(self):
        """
        equality → comparison ( ( "!=" | "==" ) comparison )*
        
        处理相等性比较表达式
        
        Returns:
            Expr: 表达式对象
        """
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
            
        return expr
    
    def comparison(self):
        """
        comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )*
        
        处理比较表达式
        
        Returns:
            Expr: 表达式对象
        """
        expr = self.term()
        
        while self.match(
            TokenType.GREATER, TokenType.GREATER_EQUAL,
            TokenType.LESS, TokenType.LESS_EQUAL
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
            
        return expr
    
    def term(self):
        """
        term → factor ( ( "-" | "+" ) factor )*
        
        处理加减法表达式
        
        Returns:
            Expr: 表达式对象
        """
        expr = self.factor()
        
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
            
        return expr
    
    def factor(self):
        """
        factor → unary ( ( "/" | "*" ) unary )*
        
        处理乘除法表达式
        
        Returns:
            Expr: 表达式对象
        """
        expr = self.unary()
        
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
            
        return expr
    
    def unary(self):
        """
        解析一元表达式
        
        语法规则：
        unary → ( "!" | "-" ) unary | call ;
        
        Returns:
            Expr: 表达式对象
            
        Raises:
            ParseError: 解析错误时抛出
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
            
        return self.call()
    
    def primary(self):
        """
        解析基本表达式
        
        primary → "true" | "false" | "nil" | "this" | NUMBER | STRING | IDENTIFIER | "(" expression ")" | "super" "." IDENTIFIER ;

        Returns:
            Expr: 表达式对象
        """
        if self.match(TokenType.TRUE):
            return Literal(True)
            
        if self.match(TokenType.FALSE):
            return Literal(False)
            
        if self.match(TokenType.NIL):
            return Literal(None)
            
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
            
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, "期望'.'在'super'后。")
            method = self.consume(TokenType.IDENTIFIER, "期望超类方法名。")
            return Super(keyword, method)
            
        if self.match(TokenType.THIS):
            return This(self.previous())
            
        if self.match(TokenType.IDENTIFIER):
            var = Variable(self.previous())
            
            # 检查是否正在解析变量声明的初始化表达式
            # 这只是一个简单的启发式方法，不能处理所有情况
            if (self.current > 0 and 
                self.tokens[self.current - 2].type == TokenType.VAR and
                self.tokens[self.current - 1].type == TokenType.EQUAL):
                # 标记为对外部变量的引用
                var._is_outer_ref = True
                
            return var
            
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "期望 ')' 在表达式后。")
            return Grouping(expr)
            
        # 解析匿名函数（Lambda表达式）
        if self.match(TokenType.FUN):
            return self.lambda_expression()
            
        # 没有匹配到任何有效的基本表达式
        raise self.error(self.peek(), "期望表达式。")
    
    def lambda_expression(self):
        """
        解析Lambda表达式（匿名函数）
        
        语法规则：
        lambda → "fun" "(" parameters? ")" block ;
        
        Returns:
            Lambda: Lambda表达式对象
            
        Raises:
            ParseError: 解析错误时抛出
        """
        self.consume(TokenType.LEFT_PAREN, "Lambda表达式后需要'('。")
        
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "函数参数不能超过255个。")
                    
                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "期望参数名。")
                )
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "参数列表后需要')'。")
        
        # 解析函数体
        self.consume(TokenType.LEFT_BRACE, "Lambda表达式需要'{'开始的函数体。")
        body = self.block()
        
        return Lambda(parameters, body)
    
    def call(self):
        """
        解析函数调用表达式
        
        call → primary ( "(" arguments? ")" | "." IDENTIFIER )*
        
        Returns:
            Expr: 函数调用表达式
        """
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "期望属性名。")
                expr = Get(expr, name)
            else:
                break
                
        return expr
        
    def finish_call(self, callee):
        """
        完成函数调用解析
        
        解析参数列表并创建调用表达式。
        
        Args:
            callee: Expr, 被调用的表达式
            
        Returns:
            Call: 函数调用表达式
            
        Raises:
            ParseError: 解析错误时抛出
        """
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "函数参数不能超过255个。")
                    
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        paren = self.consume(TokenType.RIGHT_PAREN, "期望参数后的')'。")
        
        return Call(callee, paren, arguments)
    
    def match(self, *types):
        """
        检查当前标记是否匹配指定的任一类型，如果匹配则消费该标记
        
        Args:
            *types: 要匹配的标记类型
            
        Returns:
            bool: 是否匹配成功
        """
        for type in types:
            if self.check(type):
                self.advance()
                return True
                
        return False
    
    def check(self, type):
        """
        检查当前标记是否为指定类型
        
        Args:
            type: 要检查的标记类型
            
        Returns:
            bool: 是否为指定类型
        """
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def advance(self):
        """
        消费当前标记并返回
        
        Returns:
            Token: 消费的标记
        """
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        """
        检查是否到达标记列表末尾
        
        Returns:
            bool: 是否到达末尾
        """
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        """
        返回当前标记而不消费
        
        Returns:
            Token: 当前标记
        """
        return self.tokens[self.current]
    
    def previous(self):
        """
        返回最近消费的标记
        
        Returns:
            Token: 前一个标记
        """
        return self.tokens[self.current - 1]
    
    def consume(self, type, message):
        """
        验证当前标记是否为指定类型，如果是则消费，否则报错
        
        Args:
            type: 期望的标记类型
            message: 错误信息
            
        Returns:
            Token: 消费的标记
            
        Raises:
            ParseError: 当前标记不是期望类型时抛出
        """
        if self.check(type):
            return self.advance()
            
        raise self.error(self.peek(), message)
    
    def error(self, token, message):
        """
        报告解析错误
        
        Args:
            token: 错误标记
            message: 错误信息
            
        Returns:
            ParseError: 解析错误异常
        """
        from pylox.lox import Lox
        Lox.error_token(token, message)
        return ParseError()
    
    def synchronize(self):
        """
        错误恢复，跳过标记直到下一个语句开始
        
        在解析错误后，跳过标记直到找到下一个可能是语句开始的标记。
        这有助于避免一个语法错误导致连锁反应产生更多错误。
        """
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
                
            if self.peek().type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN
            ):
                return
                
            self.advance()

    def class_declaration(self):
        """
        解析类声明
        
        classDecl → "class" IDENTIFIER ( "<" IDENTIFIER )? "{" method* "}"
        
        其中：
        - method: 
          - 普通方法: method_name(params) { body }
          - 静态方法: class method_name(params) { body }
          - getter方法: method_name { body }，没有参数列表
        
        Returns:
            Class: 类声明语句
        """
        name = self.consume(TokenType.IDENTIFIER, "期望类名。")
        
        superclass = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "期望父类名。")
            superclass = Variable(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "期望 '{' 在类体前。")
        
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            # 检查是否是静态方法 (class关键字)
            is_static = self.match(TokenType.CLASS)
            
            # 解析方法（getter或普通方法由function_declaration判断）
            method = self.function_declaration("method", is_static)
            methods.append(method)
            
        self.consume(TokenType.RIGHT_BRACE, "期望 '}' 在类体后。")
        
        return Class(name, superclass, methods)