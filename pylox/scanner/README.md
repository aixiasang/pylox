# Scanner 模块 🔍

Scanner（词法分析器）模块负责将源代码字符串转换为一系列标记（Token），这是编译或解释过程的第一步。它识别关键字、标识符、字面量和运算符等语法元素，为后续的语法分析做准备。

## 核心组件 🧩

### `scanner.py` - 词法分析器 🔎

实现了词法分析的主要逻辑:

- `Scanner` 类 - 将源代码转换为token序列
- 字符级别的源代码处理
- 复杂词素的识别和处理
- 错误处理和报告

### `token.py` - 标记定义 🏷️

定义了标记的数据结构:

- `Token` 类 - 表示一个词法单元
- 关键字、标识符、字面量和运算符的表示
- 位置信息(行号)追踪

### `token_type.py` - 标记类型 📋

定义了所有支持的标记类型:

- 关键字 - `if`, `else`, `while`, `for`, `fun`, `class` 等 🔑
- 运算符 - `+`, `-`, `*`, `/`, `==`, `!=` 等 ➕
- 标点符号 - `;`, `,`, `(`, `)`, `{`, `}` 等 📌 
- 字面量类型 - `NUMBER`, `STRING`, `IDENTIFIER` 等 📝
- 特殊类型 - `EOF` ⏹️

## 扫描过程 🔄

Scanner的工作流程:

1. **初始化** - 接收源代码并初始化内部状态 🚀
2. **扫描循环** - 逐字符处理源代码 🔁
   - 处理空白字符 ⌴
   - 识别单字符标记 (`.`, `,`, `;` 等)
   - 识别可能是一个或两个字符的标记 (`=` 或 `==`, `!` 或 `!=` 等)
   - 识别字符串字面量 (引号包围的文本)
   - 识别数字字面量
   - 识别标识符或关键字
3. **添加标记** - 创建Token对象并添加到结果列表 ➕
4. **完成** - 添加EOF标记并返回完整的标记列表 ⏹️

## 错误处理 ⚠️

Scanner能处理多种词法错误:

- **未闭合的字符串** - 字符串缺少结束引号
- **非法字符** - 源码中出现的未知字符
- **未闭合的块注释** - 缺少 `*/` 结束符的注释块

## 扩展功能 🌟

- **C风格注释支持** - 支持单行 `//` 和多行 `/* */` 注释
- **浮点数字面量** - 支持小数点和整数部分的数字表示

## 使用示例 📋

```python
from pylox.scanner import Scanner

# 创建扫描器实例
source = "var answer = 42;"
scanner = Scanner(source)

# 扫描token
tokens = scanner.scan_tokens()

# 打印所有token
for token in tokens:
    print(token)

# 输出:
# Token(VAR 'var' None 1)
# Token(IDENTIFIER 'answer' None 1)
# Token(EQUAL '=' None 1)
# Token(NUMBER '42' 42.0 1)
# Token(SEMICOLON ';' None 1)
# Token(EOF '' None 1)
```