# 面向对象设计与构造第一次作业

## 题目描述

本次作业需要完成的任务为：读入一个包含加、减、乘、乘方以及括号（其中括号的**深度至多为 1 层**）的**单变量**表达式，输出**恒等变形展开所有括号后**的表达式。

在本次作业中，**展开所有括号**的定义是：对原输入表达式 **_E_** 做**恒等变形**，得到新表达式 **_E'_**，且 **_E'_** 中不含有字符 `(` `、` `)`和空白字符 。

## 相关概念

### 基本概念的声明

* **带符号整数** **支持前导 0** 的**十**进制带符号整数（若为正数，则正号可以省略），无进制标识。如： `+02`、`-16`、`20220928`等。
* **因子**
  * **变量因子**
    * **幂函数**<br>
    _一般形式_ 由自变量 `x`，指数符号 `^` 和指数组成，指数为一个**非负**带符号整数，如：`x ^ +2`,`x ^ 02`,`x ^ 2` 。  
    _省略形式_ 当指数为 1 的时候，可以省略指数符号 `^` 和指数，如：`x` 。
  * **常数因子**
  包含一个带符号整数，如：`233` 。
  * **表达式因子**
  用一对小括号包裹起来的表达式，可以带指数，且指数为一个**非负**带符号整数，例如 `(x^2 + 2*x + x)^2` 。
* **项**
由乘法运算符连接若干因子组成，如 `x * 02`。此外，**在第一个因子之前，可以带一个正号或者负号**，如 `+ x * 02`、`- +3 * x`。注意，**空串不属于合法的项**。
* **表达式**
由加法和减法运算符连接若干项组成，如： `-1 + x ^ 233 - x ^ 06 +x` 。此外，**在第一项之前，可以带一个正号或者负号，表示第一个项的正负**，如：`- -1 + x ^ 233`、`+ -2 + x ^ 19911226`。注意，**空串不属于合法的表达式**。
* **空白字符**
空白字符包含且仅包含空格 `<space>`（ascii 值 32）和水平制表符 `\t`（ascii 值 9）。其他的空白字符，均属于非法字符。
  * 带符号整数内不允许包含空白字符，注意**符号与整数之间**也不允许包含空白字符。
  * 因子、项、表达式，在不与前两条条件矛盾的前提下，可以在任意位置包含任意数量的空白字符。

### 设定的形式化表述

* 表达式 → 空白项 [加减 空白项] 项 空白项 | 表达式 加减 空白项 项 空白项
* 项 → [加减 空白项] 因子 | 项 空白项 '*' 空白项 因子
* 因子 → 变量因子 | 常数因子 | 表达式因子
* 变量因子 → 幂函数
* 常数因子 → 带符号的整数
* 表达式因子 → '(' 表达式 ')' [空白项 指数]
* 幂函数 → 'x' [空白项 指数]
* 指数 → '^' 空白项 ['+'] 允许前导零的整数 (注：指数一定不是负数)
* 带符号的整数 → [加减] 允许前导零的整数
* 允许前导零的整数 → ('0'|'1'|'2'|…|'9'){'0'|'1'|'2'|…|'9'}
* 空白项 → {空白字符}
* 空白字符 → （空格） | \t
* 加减 → '+' | '-'

其中

* `{}` 表示允许存在 0 个、1 个或多个。
* `[]` 表示允许存在 0 个或 1 个。
* `()` 内的运算拥有更高优先级，类似数学中的括号。
* `|` 表示在多个之中选择一个。
* 上述表述中使用单引号包裹的串表示字符串字面量，如 '(' 表示字符 `(`。

## 输入/输出说明

### 输入格式

输入数据**仅包含一行**，表示待展开括号的表达式。

### 输出格式

输出展开括号之后的表达式。

### 数据限制

* 输入表达式**一定满足**基本概念部分给出的**形式化描述**。
* 输入表达式中**至多包含1层括号**。
* 对于规则 “指数 → ^ 空白项 带符号的整数” ，我们保证**此处的带符号整数中不会出现 - 号**，且保证**输入数据的指数最大不超过 8**。
* 在表达式化简过程中，如果遇到了需要计算`0^0`的值进行化简的这种情况，默认`0^0 = 1`。
* 输入表达式的**有效长度**至多为 200 个字符。其中输入表达式的**有效长度**指的是输入表达式去除掉所有**空白符**后剩余的字符总数。
* 根据文法可以注意到，整数的范围并不一定在`int`或`long`范围内。