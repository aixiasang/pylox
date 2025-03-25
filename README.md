# PyLox 项目 🚀

PyLox 是 Lox 编程语言的 Python 实现，基于 [Crafting Interpreters](https://craftinginterpreters.com/) 书籍中的设计。这是一个完整的解释器，支持变量、函数、闭包、类和继承等现代编程语言特性。

## 主要特性 ✨

- **完整的语法解析** - 词法分析和语法分析 🧩
- **丰富的表达式** - 算术、逻辑、比较和赋值 📊
- **控制流语句** - if-else, while, for, break 🔀
- **函数** - 声明、调用、递归和闭包 🧩
- **面向对象** - 类、方法、继承和this引用 🏛️
- **扩展特性** - lambda函数和BETA风格继承 🌟

## 项目结构 📂

```
pylox/
├── pylox/               # 主包
│   ├── scanner/         # 词法分析
│   ├── parser/          # 语法分析
│   ├── syntax_tree/     # 抽象语法树
│   ├── resolver/        # 变量解析
│   ├── interpreter/     # 解释执行
│   ├── lox.py           # 入口点
│   ├── environment.py   # 环境和作用域管理
│   ├── cli.py           # 命令行界面
│   └── __init__.py      # 包初始化
├── tests/               # 测试目录
└── examples/            # 示例程序
```

## 使用方法 📋

### 安装

```bash
# 克隆仓库
git clone https://github.com/aixiasang/pylox.git
cd pylox

# 安装依赖
pip install -e .

# 运行解释器
python -m pylox.lox [script]
```

### 交互式模式 (REPL)

```bash
python -m pylox.lox
> var greeting = "Hello, World!";
> print greeting;
Hello, World!
```

### 运行脚本

```bash
python -m pylox.lox examples/simple_test.lox
```

### 调试模式

```bash
python -m pylox.lox --debug examples/simple_test.lox
```

## Lox 语言示例 📝

### 变量和表达式

```lox
var a = 1;
var b = 2;
print a + b;  // 输出: 3
```

### 控制流

```lox
var a = 10;
if (a > 5) {
  print "a is greater than 5";
} else {
  print "a is less than or equal to 5";
}

// 循环
var i = 0;
while (i < 5) {
  print i;
  i = i + 1;
}
```

### 函数

```lox
fun fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 2) + fibonacci(n - 1);
}

print fibonacci(10);  // 输出: 55
```

### 闭包

```lox
fun makeCounter() {
  var count = 0;
  fun counter() {
    count = count + 1;
    return count;
  }
  return counter;
}

var counter = makeCounter();
print counter();  // 输出: 1
print counter();  // 输出: 2
```

### 类和继承

```lox
class Animal {
  init(name) {
    this.name = name;
  }
  
  speak() {
    print "Animal speaks";
  }
}

class Dog < Animal {
  init(name, breed) {
    super.init(name);
    this.breed = breed;
  }
  
  speak() {
    print this.name + " barks";
  }
  
  describe() {
    print this.name + " is a " + this.breed;
  }
}

var dog = Dog("Rex", "German Shepherd");
dog.speak();     // 输出: Rex barks
dog.describe();  // 输出: Rex is a German Shepherd
```

### BETA风格继承 (扩展特性) 🔽

与传统的继承不同，BETA风格继承允许父类控制执行流，并调用子类的实现：

```lox
class Shape {
  area() {
    print "Calculating area...";
    inner();  // 调用子类的area实现
    print "Area calculated.";
  }
}

class Circle < Shape {
  init(radius) {
    this.radius = radius;
  }
  
  area() {
    print 3.14 * this.radius * this.radius;
  }
}

var circle = Circle(5);
circle.area();
// 输出:
// Calculating area...
// 78.5
// Area calculated.
```

## 贡献 🤝

欢迎贡献代码和改进！请随时提交问题或拉取请求。