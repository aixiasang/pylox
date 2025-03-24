# Syntax Tree 模块 🌳

Syntax Tree模块定义了抽象语法树(AST)的结构，用于表示Lox程序的语法结构。这是解析过程的核心数据结构，连接Parser和Interpreter。

## 核心组件 🧩

### `expr.py` - 表达式类 📊

定义了所有表达式类型，所有这些类型都继承自抽象基类`Expr`:

- `Literal` - 字面量表达式 (数字、字符串、布尔值、nil) 📝
- `Grouping` - 分组表达式 `(...)` 🔄
- `Unary` - 一元表达式 (`!`, `-`) ➖
- `Binary` - 二元表达式 (`+`, `-`, `*`, `/`, `==`, `!=`, `<`, `<=`, `>`, `>=`) ➗
- `Variable` - 变量引用 🏷️
- `Assign` - 赋值表达式 🔄
- `Logical` - 逻辑表达式 (`and`, `or`) 🧠
- `Call` - 函数调用 📞
- `Lambda` - 匿名函数 λ
- `Get` - 属性访问 🔑
- `Set` - 属性设置 ✏️
- `This` - this表达式 👆
- `Inner` - inner表达式 (BETA风格继承) 🔽

### `stmt.py` - 语句类 📋

定义了所有语句类型，所有这些类型都继承自抽象基类`Stmt`:

- `Expression` - 表达式语句 📊
- `Print` - 打印语句 🖨️
- `Var` - 变量声明 📦
- `Block` - 块语句 `{...}` 📚
- `If` - 条件语句 🔀
- `While` - 循环语句 🔄
- `Break` - 中断语句 ⏹️
- `Function` - 函数声明 🧩
- `Return` - 返回语句 ↩️
- `Class` - 类声明 🏛️

### `visitor.py` - 访问者模式 👁️

实现了访问者模式接口，使得不同的操作（如解释执行、打印、静态分析）可以在不修改AST类的情况下添加：

- `Visitor` - 访问者接口 🔍

### `ast_printer.py` - AST打印器 🖨️

用于将AST转换为可读的字符串格式，便于调试：

- `AstPrinter` - 实现了Visitor接口的AST打印器 📝

## 设计模式 🧮

- **访问者模式** - 将操作与数据结构分离
- **组合模式** - 表达式和语句的树状结构
- **解释器模式** - AST节点表示语言元素

## 使用示例 📋

### 手动构建表达式

```python
from pylox.syntax_tree import Binary, Literal, Unary
from pylox.scanner.token import Token
from pylox.scanner.token_type import TokenType
from pylox.syntax_tree.ast_printer import AstPrinter

# 构建 -(2 + 3) 表达式
expr = Unary(
    Token(TokenType.MINUS, "-", None, 1),
    Grouping(
        Binary(
            Literal(2),
            Token(TokenType.PLUS, "+", None, 1),
            Literal(3)
        )
    )
)

# 打印表达式
printer = AstPrinter()
print(printer.print(expr))  # 输出: -(group (+ 2 3))
```

### 通过解析器构建AST

```python
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.syntax_tree.ast_printer import AstPrinter

# 源代码
source = "-(2 + 3);"

# 扫描和解析
scanner = Scanner(source)
tokens = scanner.scan_tokens()
parser = Parser(tokens)
statements = parser.parse()

# 打印第一个语句的表达式
printer = AstPrinter()
print(printer.print(statements[0].expression))  # 输出: -(group (+ 2 3))
```