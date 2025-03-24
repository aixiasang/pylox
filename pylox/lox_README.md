# Lox 主入口模块 (lox.py) 🚪

`lox.py` 是整个 PyLox 解释器的入口点和核心控制模块，负责启动解释器，处理命令行参数，运行脚本文件或启动交互式 REPL 环境。这个模块连接 Scanner、Parser、Resolver 和 Interpreter 各个组件，构成完整的解释器流程。

## 核心功能 🧩

### 解释器启动和控制 🎮

- `run` 方法 - 执行 Lox 源代码的核心方法
- `run_file` 方法 - 从文件加载并执行 Lox 代码
- `run_prompt` 方法 - 启动交互式 REPL 环境
- 命令行参数处理 - 处理各种运行模式和选项

### 错误处理和报告 ⚠️

- 语法错误报告和处理
- 运行时错误捕获和显示
- 行号和位置追踪
- 错误状态管理

## 解释器流程 🔄

Lox 解释器的完整执行流程:

1. **源代码输入** - 从文件或用户输入获取源代码 📝
2. **词法分析** - 使用 Scanner 将源代码转换为 token 序列 🔍
3. **语法分析** - 使用 Parser 将 token 序列转换为抽象语法树 (AST) 🧩
4. **变量解析** - 使用 Resolver 解析变量引用和作用域 🔎
5. **解释执行** - 使用 Interpreter 执行 AST 🚀
6. **结果输出** - 显示执行结果或错误信息 📊

## 命令行参数 🛠️

支持的命令行选项:

- **无参数** - 启动交互式 REPL 环境
- **文件路径** - 执行指定的 Lox 脚本文件
- `--debug` - 启用调试模式，显示更多详细信息
- `--no-resolver` - 跳过变量解析阶段 (仅用于调试)
- `--ast-print` - 打印解析生成的抽象语法树

## 异常处理 🚨

处理两种主要类型的错误:

1. **语法错误** - 在扫描和解析阶段检测到的错误
   ```
   [line 5] Error: Expect ')' after arguments.
   ```

2. **运行时错误** - 执行期间发生的错误
   ```
   [line 10] RuntimeError: Undefined variable 'x'.
   ```

## 调试支持 🐛

调试功能包括:

- 源代码追踪和显示
- Token 序列打印
- AST 结构可视化
- 解释器状态跟踪
- 变量解析信息

## 使用示例 📋

### 执行脚本文件

```bash
# 基本用法
python -m pylox.lox examples/hello.lox

# 调试模式
python -m pylox.lox --debug examples/hello.lox
```

### 交互式 REPL 环境

```bash
python -m pylox.lox
> var x = 10;
> var y = 20;
> print x + y;
30
> fun greet(name) { print "Hello, " + name + "!"; }
> greet("world");
Hello, world!
> exit
```

## REPL 特性 🖥️

交互式环境的特点:

- **逐行执行** - 每行输入都会立即执行 ⚡
- **变量保持** - 变量在会话期间保持其值 🔄
- **特殊命令** - 支持 `exit` 或 Ctrl+D 退出 ❌
- **多行表达式** - 不完整的表达式会等待更多输入 📝