---
date:
    created: 2024-10-15
---
# P1：课上考试总结

## Q1 数据比较

输入两个32位数a、b，输出cnt表示分别以a**从右到左**和b**从左到右**按位比较不相同位数的个数。

|    信号名    |方向|描述|
|:---------:|:---:|:-----:|
| a [31:0]  |I|第一个数|
| b [31:0]  |I|第二个数|
| cnt [5:0] |O|比较位数结果|

本题其实很简单，就是将a[i]和b[31-i]分别比较一下是否相等即可， <del>不用动脑子写32行就行，</del>
但这道题实实在在坑了我很久，即使现在我仍然要再重新理解Verilog的运行逻辑。

```verilog
reg [5:0] count;
	
integer i;
always @(a,b)
begin
    count=0;
    for(i=0;i<32;i=i+1)
    begin
        count=(a[i+:1]^b[31-i+:1])?count+1:count;
    end
end
	
assign cnt=count;
```
以上的代码有几点值得注意：

* **不能直接用a[i]表示数据a的第i位**
  > 在普通的位选中，高位和低位都必须是常量，也就是说，没办法让类似循环一类的东西辅助位选，因此有如下规范：
  > <pre><code>big_vect[lsb_base_expr +: width_expr];
  > big_vect[msb_base_expr -: width_expr];
  > //a[0 +: 4] 就是 a[3:0]
  > //a[7 -: 4] 就是 a[7:4]</code></pre>
  > 在这种方法中，位选基准位可以是变量，只要宽度是常量就可以了。
* **`integer i`必须在always块外定义**  
  否则将会导致无法仿真<del>，但我也不清楚为什么Behavioral Check Syntax不会报错</del>。
* **初始化`count=0`是必须的**  
  否则将会导致输出cnt成为xxx错误。