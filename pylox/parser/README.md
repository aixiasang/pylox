# Parser 模块 🧩

Parser（语法分析器）模块负责将token序列转换为抽象语法树(AST)，实现Lox语言的语法分析功能。它采用递归下降解析技术，按照Lox语言的语法规则构建程序的结构表示。

## 核心组件 🎯

### `parser.py` - 递归下降解析器 🔍

实现了完整的Lox语言语法解析:

- `Parser` 类 - 主解析器类，将token流转换为AST
- 表达式解析 - 解析各种表达式结构
- 语句解析 - 解析各种语句结构
- 错误处理 - 语法错误的检测和恢复

## Lox语言语法 📝

### 表达式解析 📊

Parser能解析的表达式包括:

- 字面量 (数字、字符串、布尔值、nil) 📝
- 一元表达式 (`!`, `-`) ➖
- 二元表达式 (`+`, `-`, `*`, `/`, `==`, `!=`, `<`, `<=`, `>`, `>=`) ➗
- 分组表达式 `(...)` 🔄
- 变量引用 🏷️
- 赋值表达式 🔄
- 逻辑表达式 (`and`, `or`) 🧠
- 函数调用 📞
- 匿名函数 (lambda) λ
- 属性访问 `.` 🔑
- 属性设置 🖊️
- `this` 表达式 👆
- `super` 表达式 👨‍👦
- `inner` 表达式 (BETA风格继承) 🔽

### 语句解析 📋

Parser能解析的语句包括:

- 表达式语句 📊
- 打印语句 `print` 🖨️
- 变量声明 `var` 📦
- 块语句 `{...}` 📚
- 条件语句 `if` 🔀
- 循环语句 `while`, `for` 🔄
- 中断语句 `break` ⏹️
- 函数声明 `fun` 🧩
- 返回语句 `return` ↩️
- 类声明 `class` 🏛️

### 语法优先级 ⚖️

Lox语言的表达式按照以下优先级（从高到低）解析:

1. 基本表达式：字面量、分组、变量、`this`, `super` 📝
2. 函数调用和属性访问 📞
3. 一元表达式 `-`, `!` ➖
4. 乘法/除法 `*`, `/` ✖️
5. 加法/减法 `+`, `-` ➕
6. 比较 `>`, `>=`, `<`, `<=` ⚖️
7. 相等 `==`, `!=` 🟰
8. 逻辑与 `and` 🔄
9. 逻辑或 `or` 🔀
10. 赋值 `=` 📝

## 错误处理 ⚠️

Parser实现了强大的错误处理机制：

- `ParseError` 异常 - 表示语法错误
- 同步恢复 - 在发生错误后尝试恢复并继续解析
- 精确的错误位置和信息 - 帮助用户定位和理解错误

## 特殊功能 🌟

- **Lambda表达式** - 匿名函数支持 λ
- **BETA风格继承** - 除了传统的继承模型外，还支持BETA风格继承 🔽
- **同步恢复** - 在检测到语法错误后，尝试同步到语句边界并继续解析，以便一次解析发现多个错误

## 使用示例 📋

```python
from pylox.scanner import Scanner
from pylox.parser import Parser

# 源代码
source = """
fun factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}

print factorial(5);
"""

# 扫描和解析
scanner = Scanner(source)
tokens = scanner.scan_tokens()
parser = Parser(tokens)
statements = parser.parse()

# 现在statements包含了AST表示
```

## AST结构示例 🌳

输入Lox代码:

```lox
print 2 + 3 * 4;
```

生成的AST:

```
Print
  └─ Binary(+)
      ├─ Literal(2)
      └─ Binary(*)
          ├─ Literal(3)
          └─ Literal(4)
```