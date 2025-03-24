# 解析和绑定实现文档

## 1. 问题背景

在实现变量访问和作用域时，我们使用了环境链来查找变量。在基本情况下这种方法可以工作，但在涉及闭包时，会出现一些微妙的问题：

```lox
var a = "global";
{
  fun showA() {
    print a;
  }
  
  showA();  // 输出: "global"
  var a = "block";
  showA();  // 应该输出: "global"，但在之前的实现中会输出 "block"
}
```

问题在于，简单的环境链实现会在函数执行时查找变量，而不是在函数定义时。这违反了词法作用域（lexical scoping）规则，词法作用域要求变量引用应该基于函数定义时的环境，而非调用时的环境。

## 2. 解决方案：变量解析

为了解决这个问题，我们引入了**变量解析**过程，这是一个在执行前的静态分析阶段，用于确定每个变量引用应该绑定到哪个声明。

解析过程的主要任务是：
1. 跟踪变量的声明和作用域
2. 确定每个变量引用应该解析到哪个声明
3. 检测变量自引用等错误

## 3. 实现详情

### 3.1 Resolver类

`Resolver`类是一个访问者（Visitor），用于遍历AST并记录变量信息：

```python
class Resolver(Visitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter  # 将结果传递给解释器
        self.scopes = []  # 作用域栈，每个作用域是变量名到布尔值的映射
        self.current_function = FunctionType.NONE  # 当前函数类型
```

### 3.2 作用域管理

Resolver使用一个栈来管理嵌套的作用域，每个作用域是一个字典，键为变量名，值为布尔值表示变量是否已完成初始化：

```python
def begin_scope(self):
    self.scopes.append({})

def end_scope(self):
    self.scopes.pop()
```

### 3.3 变量声明和定义

变量处理分为两个阶段：
1. **声明**：将变量添加到作用域，但标记为"未初始化"
2. **定义**：标记变量为"已初始化"，可以安全使用

这允许我们检测到变量自引用等错误：

```python
def declare(self, name):
    if not self.scopes:
        return  # 全局作用域
    
    scope = self.scopes[-1]
    
    # 检查变量是否已在当前作用域中声明
    if name.lexeme in scope:
        Lox.error(name, f"已经在此作用域中声明了变量'{name.lexeme}'。")
    
    # 标记为"声明但未初始化"
    scope[name.lexeme] = False

def define(self, name):
    if not self.scopes:
        return
    
    # 标记为"已初始化"
    self.scopes[-1][name.lexeme] = True
```

### 3.4 变量解析

解析变量引用是核心功能，它确定变量引用与其声明之间的关系：

```python
def resolve_local(self, expr, name):
    # 从内到外查找变量声明
    for i in range(len(self.scopes) - 1, -1, -1):
        if name.lexeme in self.scopes[i]:
            # 计算并存储"距离"（环境深度）
            self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
            return
```

### 3.5 函数与闭包处理

函数处理需要创建新的作用域，处理参数，然后解析函数体：

```python
def resolve_function(self, function, type):
    enclosing_function = self.current_function
    self.current_function = type
    
    self.begin_scope()
    
    for param in function.params:
        self.declare(param)
        self.define(param)
    
    self.resolve(function.body)
    
    self.end_scope()
    
    self.current_function = enclosing_function
```

## 4. 解释器修改

解释器也需要做出相应修改，以使用Resolver提供的信息：

### 4.1 存储解析结果

```python
def __init__(self):
    self.globals = Environment()
    self.environment = self.globals
    self.locals = {}  # 存储变量引用的解析结果

def resolve(self, expr, depth):
    self.locals[expr] = depth
```

### 4.2 变量查找

使用解析结果查找变量，确保闭包正确捕获变量：

```python
def look_up_variable(self, name, expr):
    distance = self.locals.get(expr)
    if distance is not None:
        return self.environment.get_at(distance, name.lexeme)
    else:
        return self.globals.get(name)
```

### 4.3 修改Environment类

`Environment`类需要添加方法来支持访问指定深度的环境：

```python
def get_at(self, distance, name):
    return self.ancestor(distance).values.get(name)

def ancestor(self, distance):
    environment = self
    for i in range(distance):
        environment = environment.enclosing
    
    return environment
```

## 5. 解析和绑定的好处

实现解析和绑定带来了几个重要好处：

1. **正确的词法作用域**：确保变量引用遵循词法作用域规则，特别是在闭包中
2. **提前错误检测**：可以在执行前检测到变量自引用等错误
3. **性能优化**：减少运行时的变量查找开销，特别是对于深层嵌套的作用域
4. **为未来特性铺路**：为类、继承、静态分析等功能打下基础

## 6. 测试结果

我们的解析器能够成功处理以下情况：

- 基本变量访问和遮蔽
- 函数中变量的正确解析
- 闭包正确捕获环境中的变量
- 检测变量自引用错误
- 确保词法作用域在所有情况下的正确性

## 7. 结论

解析和绑定是实现词法作用域的关键步骤，它确保了变量引用的一致性和正确性。这种两阶段的方法（先静态分析，再执行）是许多语言实现中的常见模式，为我们提供了更强大的错误检测和优化机会。在Lox语言中，它解决了闭包中变量捕获的问题，确保了语言行为的一致性和可预测性。