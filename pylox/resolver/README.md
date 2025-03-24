# Resolver 模块 🔍

Resolver模块负责在解释执行之前进行静态分析，解析变量作用域和引用，从而提供更高效的变量查找和更准确的错误检测。

## 核心组件 🧩

### `resolver.py` - 变量解析器 🔎

解析变量引用和作用域:

- `Resolver` 类 - 实现了`ExprVisitor`和`StmtVisitor`接口
- 作用域堆栈管理 - 追踪局部变量和嵌套作用域
- 变量声明和引用解析
- 错误检测

## 功能特性 🌟

### 1. 变量解析 🏷️

- 记录每个变量引用对应的声明位置
- 解析嵌套作用域中的变量
- 为解释器提供变量访问的优化信息

### 2. 上下文检查 🔍

- 验证`return`语句只出现在函数中 ↩️
- 验证`this`只在类方法中使用 👆
- 验证`super`只在子类方法中使用，且父类存在 👨‍👦
- 验证`inner`只在继承体系的合适位置使用 🔽
- 验证`break`只在循环中使用 ⏹️

### 3. 错误检测 ⚠️

- 检测变量自引用 (如 `var a = a;`) 🔄
- 检测重复变量声明 🔄
- 检测未初始化的变量访问 ❓
- 检测类的自我继承 (如 `class A < A {}`) 🔄
- 检测无效的`super`访问 ❌

### 4. 作用域管理 🌍

- 全局作用域
- 函数作用域
- 块作用域
- 类作用域
- 方法作用域

### 5. 优化准备 🚀

- 变量查找优化 - 使解释器可以直接跳转到正确的环境
- 闭包准备 - 标记需要作为闭包捕获的变量

## 解析过程 📋

1. **开始作用域** - 当进入新块时，将新作用域压入栈 📥
2. **声明变量** - 记录变量在当前作用域中的声明 📝
3. **定义变量** - 标记变量为已初始化，可以被使用 ✅
4. **解析变量** - 查找变量声明并记录作用域距离 🔍
5. **解析函数** - 处理函数参数和函数体 📞
6. **解析类** - 处理类方法和继承 🏛️
7. **结束作用域** - 当离开块时，将作用域弹出栈 📤

## 作用域距离 📏

Resolver计算并记录每个变量引用到其声明的"距离"：

- 距离为0 - 当前作用域中的变量
- 距离为1 - 外层作用域中的变量
- 距离为n - n层外层作用域中的变量

这些距离信息使解释器能够直接跳转到正确的环境进行变量查找，不需要逐层搜索。

## 使用示例 📋

```python
from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.resolver import Resolver
from pylox.interpreter import Interpreter

# 源代码
source = """
var a = "global";
{
  var a = "shadow";
  print a;
}
print a;
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
interpreter.interpret(statements)
# 输出:
# shadow
# global
```

## 错误检测示例 ⚠️

```
// 变量自引用
var a = a;  // 错误: Cannot read local variable in its own initializer.

// 重复变量声明
{
  var a = 1;
  var a = 2;  // 错误: Already a variable with this name in this scope.
}

// 类自我继承
class A < A {}  // 错误: A class can't inherit from itself.

// 无效的super访问
class A {
  method() {
    super.method();  // 错误: Can't use 'super' in a class with no superclass.
  }
}

// 无效的return
return "outside";  // 错误: Can't return from top-level code.

// 无效的this
print this;  // 错误: Can't use 'this' outside of a class.

// 无效的break
break;  // 错误: Can't use 'break' outside of a loop.
```