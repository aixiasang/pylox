# Lox语言类实现文档

## 概述

本文档描述了Lox语言类系统的实现。类系统支持面向对象编程的基础特性，包括类定义、实例创建、属性访问和方法调用。

## 类型定义

类系统主要由以下AST节点类型组成：

1. **Class**：表示类声明语句
2. **Get**：表示属性访问表达式
3. **Set**：表示属性赋值表达式
4. **This**：表示`this`关键字引用

## 语法

类相关语法规则如下：

```
classDecl      → "class" IDENTIFIER "{" method* "}" ;
method         → IDENTIFIER "(" parameters? ")" block ;
parameters     → IDENTIFIER ( "," IDENTIFIER )* ;
arguments      → expression ( "," expression )* ;
primary        → "true" | "false" | "nil" | "this" | NUMBER | STRING 
               | IDENTIFIER | "(" expression ")" | "fun" "(" parameters? ")" block ;
call           → primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
assignment     → ( call "." )? IDENTIFIER "=" assignment | logic_or ;
```

## 类的表示

类在运行时表示为`LoxClass`类的实例，具有以下属性：

- `name`：类名
- `methods`：方法字典，键为方法名，值为`LoxFunction`对象

`LoxClass`实现了`LoxCallable`接口，因此可以像函数一样被调用，调用时创建该类的新实例。

## 实例的表示

实例表示为`LoxInstance`类的实例，具有以下属性：

- `klass`：实例所属的类
- `fields`：实例字段字典，键为字段名，值为字段值

实例字段动态添加，不需要在类定义中预先声明。访问不存在的字段会抛出运行时错误。

## 方法的处理

方法表示为绑定到特定实例的`LoxFunction`对象。方法绑定通过以下步骤实现：

1. 当通过实例访问方法时，从类中查找方法定义
2. 使用`LoxFunction.bind()`方法创建新函数，新函数的闭包环境中包含`this`变量
3. `this`变量绑定到当前实例

## 特殊方法：`init`

`init`方法是构造函数，类被调用时自动执行。其特殊行为包括：

1. 无论返回什么，总是返回实例本身
2. 参数数量决定创建实例时需要的参数数量

## 例子

以下是Lox类系统的使用例子：

```lox
class Counter {
  init() {
    this.count = 0;
  }

  increment() {
    this.count = this.count + 1;
    return this.count;
  }
}

var counter = Counter();
print counter.increment(); // 输出: 1
print counter.increment(); // 输出: 2
```

## 实现细节

实现类系统涉及多个组件的修改：

1. **解析器**：识别类声明、方法定义、`this`关键字和属性访问
2. **解析器**：解析类声明、方法和`this`引用的作用域
3. **解释器**：执行类声明、创建实例、访问属性和调用方法

## 未来扩展可能性

目前实现的类系统可以进一步扩展，可能的方向包括：

1. 添加继承支持
2. 添加静态方法
3. 添加访问控制（公有/私有字段和方法）
4. 添加接口和多态支持

---

*注：本文档描述了Lox语言类系统的基本实现，基于Crafting Interpreters书中的设计。*