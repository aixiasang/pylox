# Interpreter 模块 🚀

Interpreter模块是PyLox解释器的核心，负责执行抽象语法树(AST)所表示的Lox程序，实现语言的运行时行为。

## 核心组件 🧩

### `interpreter.py` - 主解释器 🎮

实现了表达式和语句的访问者接口，负责解释执行AST:

- `Interpreter` 类 - 主解释器类，实现了`ExprVisitor`和`StmtVisitor`接口
- 环境管理 - 维护变量作用域
- 运行时错误处理 - 捕获和报告运行时错误

### `environment.py` - 环境管理 🌍

定义了变量的作用域和生命周期管理:

- `Environment` 类 - 存储变量与值的映射关系
- 作用域嵌套 - 支持局部作用域和闭包
- 变量的定义、获取和赋值

### `lox_callable.py` - 可调用对象 📞

定义了函数和类方法的调用接口和实现:

- `LoxCallable` 接口 - 可调用对象的抽象接口
- `LoxFunction` 类 - 用户定义函数的实现
- `LoxStaticMethod` 类 - 静态方法
- `LoxBetaStyleMethod` 类 - BETA风格继承的方法
- `Clock` 类 - 内置函数实现示例

### `lox_class.py` - 类实现 🏛️

实现了Lox语言的面向对象特性:

- `LoxClass` 类 - 表示用户定义的类
- `LoxInstance` 类 - 表示类的实例
- 方法调用和字段访问
- 继承支持
- BETA风格继承

### `return_value.py` - 返回值处理 ↩️

特殊类用于在解释器中处理返回语句:

- `Return` 类 - 用于从函数中返回值

### `runtime_error.py` - 运行时错误 ⚠️

运行时错误的定义和处理:

- `RuntimeError` 类 - 表示运行时错误
- 错误信息和位置跟踪

## 运行时特性 🌟

### 1. 数据类型 📊

支持的基本数据类型:
- 数字(浮点数) 🔢
- 字符串 📝
- 布尔值 ✓/✗
- Nil(null) ⭕
- 函数 📞
- 类 🏛️
- 实例 🧩

### 2. 变量 🏷️

- 作用域(全局和局部) 🌍
- 闭包 📦
- 变量遮蔽(shadowing) 🕶️

### 3. 控制流 🔀

- 条件语句(`if`/`else`) ⚖️
- 循环(`while`, `for`) 🔄
- 提前终止循环(`break`) ⏹️

### 4. 函数 🧩

- 用户定义函数 📋
- 闭包 🔒
- 递归 📞📞
- 返回值处理 ↩️
- 匿名函数(Lambda) λ

### 5. 面向对象编程 🏛️

- 类定义 📝
- 实例创建 🆕
- 方法调用 📞
- 继承 👨‍👦
- 字段访问和修改 🔑
- `this` 引用 👆
- 初始化方法 🛠️
- Getter方法 🔍
- 静态方法 📊
- BETA风格继承 🔽

## 继承模型 👨‍👦

### 1. 传统继承模型
- 子类继承父类的所有方法
- 子类可以覆盖父类方法
- 使用`super`关键字访问父类方法

### 2. BETA风格继承模型 🔽
- 方法查找从顶层开始向下
- 方法执行从祖父类向下到子类
- 子类不能完全替换父类方法
- 使用`inner`关键字调用更低层级的方法

## 使用示例 📋

### 基本解释

```python
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.interpreter import Interpreter
from pylox.resolver import Resolver

# 源代码
source = """
var a = 1;
var b = 2;
print a + b;
"""

# 扫描和解析
scanner = Scanner(source)
tokens = scanner.scan_tokens()
parser = Parser(tokens)
statements = parser.parse()

# 变量解析
interpreter = Interpreter()
resolver = Resolver(interpreter)
resolver.resolve(statements)

# 解释执行
interpreter.interpret(statements)  # 输出: 3
```

### OOP示例

```python
# Lox源代码
"""
class Person {
  init(name) {
    this.name = name;
  }
  
  sayHello() {
    print "Hello, I am " + this.name + "!";
  }
}

var john = Person("John");
john.sayHello();  // 输出: Hello, I am John!
"""
```