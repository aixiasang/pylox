class Resolver(ExprVisitor, StmtVisitor):
    """
    解析器类，用于变量解析
    """
    
    # 函数类型枚举
    class FunctionType:
        NONE = "NONE"
        FUNCTION = "FUNCTION"
        INITIALIZER = "INITIALIZER"
        METHOD = "METHOD"
    
    # 类类型枚举
    class ClassType:
        NONE = "NONE"
        CLASS = "CLASS"
    
    def __init__(self, interpreter):
        """
        解析器初始化
        
        Args:
            interpreter: 解释器
        """
        self.interpreter = interpreter
        # 作用域栈
        self.scopes = []
        # 当前函数类型
        self.current_function = self.FunctionType.NONE
        # 当前类类型
        self.current_class = self.ClassType.NONE
        
    def visit_class_stmt(self, stmt):
        """
        访问类声明语句
        
        Args:
            stmt: Class, 类声明语句
            
        Returns:
            None
        """
        enclosing_class = self.current_class
        self.current_class = self.ClassType.CLASS
        
        self.declare(stmt.name)
        self.define(stmt.name)
        
        # 创建一个新的作用域用于this
        self.begin_scope()
        self.scopes[-1]["this"] = True
        
        # 解析方法
        for method in stmt.methods:
            declaration = self.FunctionType.METHOD
            # 如果是初始化方法
            if method.name.lexeme == "init":
                declaration = self.FunctionType.INITIALIZER
                
            self.resolve_function(method, declaration)
            
        # 关闭this作用域
        self.end_scope()
        
        self.current_class = enclosing_class
        return None
    
    def visit_get_expr(self, expr):
        """
        访问属性访问表达式
        
        Args:
            expr: Get, 属性访问表达式
            
        Returns:
            None
        """
        self.resolve(expr.object)
        return None
    
    def visit_set_expr(self, expr):
        """
        访问属性设置表达式
        
        Args:
            expr: Set, 属性设置表达式
            
        Returns:
            None
        """
        self.resolve(expr.value)
        self.resolve(expr.object)
        return None
    
    def visit_this_expr(self, expr):
        """
        访问this表达式
        
        Args:
            expr: This, this表达式
            
        Returns:
            None
        """
        if self.current_class == self.ClassType.NONE:
            self.lox.error(expr.keyword,
                         "无法在类外部使用'this'。")
            return None
            
        self.resolve_local(expr, expr.keyword)
        return None
    
    def resolve_function(self, function, function_type):
        """
        解析函数
        
        Args:
            function: Function, 函数声明
            function_type: FunctionType, 函数类型
        """
        enclosing_function = self.current_function
        self.current_function = function_type
        
        self.begin_scope()
        for param in function.parameters:
            self.declare(param)
            self.define(param)
            
        self.resolve(function.body)
        self.end_scope()
        
        self.current_function = enclosing_function
    
    # ... existing code ... 