# PyLox 模块 🎯

PyLox 是 Lox 解释器的 Python 实现，包含了扫描器、解析器、解释器和变量解析器等多个核心组件。此模块是整个项目的入口点，提供命令行接口来执行 Lox 代码。

## 核心组件 🧩

### `lox.py` - 主入口 🚪

这是整个解释器的入口点，用于:
- 处理命令行参数
- 提供交互式 REPL 环境
- 执行 Lox 脚本文件
- 报告错误和异常

### `error_reporter.py` - 错误报告 🚨

提供统一的错误处理和报告机制:
- 语法错误报告
- 运行时错误报告
- 行号和位置追踪
- 错误消息格式化

## 使用方法 📋

### 运行脚本文件 📜

```bash
python -m pylox.lox path/to/script.lox
```

### 启动交互式 REPL 🖥️

```bash
python -m pylox.lox
```

### 启用调试模式 🐛

```bash
python -m pylox.lox --debug path/to/script.lox
```

## 命令行参数 🛠️

- `--debug`: 启用调试模式，显示更多中间过程信息
- `--no-resolver`: 跳过变量解析阶段
- `--ast-print`: 打印解析得到的抽象语法树

## 错误处理 ⚠️

PyLox 处理两种主要类型的错误:

1. **语法错误** - 在扫描和解析阶段检测到的错误 📝
   ```
   [line 22] Error at ';': Expect ')' after arguments.
   ```

2. **运行时错误** - 执行期间发生的错误 🚨
   ```
   [line 42] RuntimeError: Undefined variable 'foo'.
   ```

## 交互式环境 (REPL) 🖥️

REPL 环境允许逐行输入和执行 Lox 代码:

```
> var a = 10;
> var b = 20;
> print a + b;
30
> print "Hello, " + "world!";
Hello, world!
```

## 模块组织 📂

PyLox 包含以下主要子模块:

- `scanner` - 词法分析器，将源代码转换为 token 序列 🔍
- `parser` - 语法分析器，将 token 序列转换为抽象语法树 🧩
- `syntax_tree` - 定义抽象语法树的结构 🌳
- `interpreter` - 执行抽象语法树，实现语言的运行时行为 🚀
- `resolver` - 变量解析和静态分析 🔎

## Lox 语言特性 ✨

PyLox 实现了完整的 Lox 语言规范，包括:

1. **基本数据类型** - 数字、字符串、布尔值、nil 📊
2. **变量和作用域** - 局部变量、闭包、变量遮蔽 🏷️
3. **控制流** - if、while、for、break 🔀
4. **函数** - 函数声明、递归、匿名函数、闭包 🧩
5. **面向对象编程** - 类、实例、方法、继承 🏛️
   - 传统继承 - 使用 `super` 关键字 👨‍👦
   - BETA 风格继承 - 使用 `inner` 关键字 🔽

## BETA 风格继承示例 🔽

BETA 风格继承是 PyLox 中一项特殊的扩展功能，与传统 OOP 继承不同:

```lox
class A {
  method() {
    print "A.method";
    inner(); // 调用子类的方法实现
  }
}

class B < A {
  method() {
    print "B.method";
  }
}

var b = B();
b.method();
// 输出:
// A.method
// B.method
```

BETA 风格继承特点:
- 方法查找从顶层开始向下
- 方法执行从祖父类向下到子类
- 子类不能完全替换父类方法
- 使用 `inner` 关键字调用更低层级的方法