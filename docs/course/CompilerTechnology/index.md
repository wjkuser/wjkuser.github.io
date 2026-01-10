### 临时文件 - 代码文件 debug 修复

#### midend\llvm_IR\instruction\PhiInstr.java

```
diff --git a/midend/llvm_IR/instruction/PhiInstr.java b/midend/llvm_IR/instruction/PhiInstr.java
index af6952a..3af1065 100644
--- a/midend/llvm_IR/instruction/PhiInstr.java
+++ b/midend/llvm_IR/instruction/PhiInstr.java
■ @@ -22,6 +22,17 @@ public class PhiInstr extends Instruction {
         }
     }

+    public PhiInstr(IRType irType, BasicBlock basicBlock, String varName) {
+        super(irType, InstructionType.PHI, varName, false);
+        this.setBasicBlock(basicBlock);
+
+        this.beforeBlockList = new ArrayList<>(basicBlock.getBeforeBlocks());
+        // 填充相应的value，等待后续替换
+        for (int i = 0; i < this.beforeBlockList.size(); i++) {
+            this.addUseValue(null);
+        }
+    }
+
     public ArrayList<BasicBlock> getBeforeBlockList() {
         return this.beforeBlockList;
     }
```

#### midend\utils\visit\DeclVisitor.java

```
diff --git a/midend/utils/visit/DeclVisitor.java b/midend/utils/visit/DeclVisitor.java
index 374c36b..4083a8d 100644
--- a/midend/utils/visit/DeclVisitor.java
+++ b/midend/utils/visit/DeclVisitor.java
■ @@ -155,6 +155,9 @@ public class DeclVisitor
 //                new StoreInstr(new ConstantInt(0), allocateInstr);
 //            }
         } else {
+            // 对于数组，需要初始化所有元素
+            int initCount = 0;  // 已初始化的元素数量
+
             if (initVal != null) {
                 // 生成一系列 GEP + store 指令，将初始值存入常量
                 ArrayList<Exp> expList = initVal.getExpList();


■ @@ -166,14 +169,14 @@ public class DeclVisitor
                     // 将初始值存储到偏移量中
                     new StoreInstr(irExp, gepInstr);
                 }
+                initCount = expList.size();
+                // 将剩余未初始化的元素初始化为 0
+                for (int i = initCount; i < symbol.getDepth(); i++) {
+                    GetelementptrInstr gepInstr = new GetelementptrInstr(allocateInstr, new ConstantInt(i));
+                    // 将初始值存储到偏移量中
+                    new StoreInstr(new ConstantInt(0), gepInstr);
+                }
             }
-//            else {
-//                for (int i = 0; i < symbol.getDepth(); i++) {
-//                    GetelementptrInstr gepInstr = new GetelementptrInstr(allocateInstr, new ConstantInt(i));
-//                    // 将初始值存储到偏移量中
-//                    new StoreInstr(new ConstantInt(0), gepInstr);
-//                }
-//            }
         }
         symbol.setValue(allocateInstr);
     }
```

#### midend\utils\Builder.java

```
diff --git a/midend/utils/Builder.java b/midend/utils/Builder.java
index 982b34c..9f06968 100644
--- a/midend/utils/Builder.java
+++ b/midend/utils/Builder.java
■ @@ -127,7 +127,15 @@ public class Builder
     }

     public static String getLocalVarName() {
-        int count = localVarCountMap.get(currentFunction);
+        if (currentFunction == null) {
+            throw new RuntimeException("Error: currentFunction is null when calling getLocalVarName()");
+        }
+        Integer count = localVarCountMap.get(currentFunction);
+        if (count == null) {
+            // 如果函数还没有计数器，初始化为0
+            count = 0;
+            localVarCountMap.put(currentFunction, count);
+        }
         localVarCountMap.put(currentFunction, count + 1);
         return LOCAL_VAR_NAME + count;
     }
```

#### optimize\InsertPhi.java

```
diff --git a/optimize/InsertPhi.java b/optimize/InsertPhi.java
index d30f3d7..d4cced4 100644
--- a/optimize/InsertPhi.java
+++ b/optimize/InsertPhi.java
■ @@ -3,6 +3,8 @@ package optimize;
 import midend.llvm_IR.constant.ConstantInt;
 import midend.llvm_IR.instruction.*;
 import midend.llvm_IR.value.BasicBlock;
+import midend.llvm_IR.value.Function;
+import midend.llvm_IR.value.Parameter;
 import midend.llvm_IR.value.Value;
 import java.util.ArrayList;


■ @@ -18,8 +20,13 @@ public class InsertPhi {
     private final ArrayList<BasicBlock> defineBlocks;
     private final ArrayList<BasicBlock> useBlocks;
     private Stack<Value> valueStack;
+    private int maxVarIndex;  // 函数中已使用的最大变量编号

     public InsertPhi(AllocaInstr allocateInstr, BasicBlock entryBlock) {
+        this(allocateInstr, entryBlock, -1);
+    }
+
+    public InsertPhi(AllocaInstr allocateInstr, BasicBlock entryBlock, int initialMaxVarIndex) {
         this.allocateInstr = allocateInstr;
         this.entryBlock = entryBlock;
         this.defineInstrs = new HashSet<>();


■ @@ -27,6 +34,16 @@ public class InsertPhi {
         this.defineBlocks = new ArrayList<>();
         this.useBlocks = new ArrayList<>();
         this.valueStack = new Stack<>();
+        // 如果提供了初始最大变量编号，使用它；否则自己查找
+        if (initialMaxVarIndex >= 0) {
+            this.maxVarIndex = initialMaxVarIndex;
+        } else {
+            this.maxVarIndex = this.findMaxVarIndex(entryBlock.getFunction());
+        }
+    }
+
+    public int getMaxVarIndex() {
+        return this.maxVarIndex;
     }

     public void addPhi() {


■ @@ -99,13 +116,62 @@ public class InsertPhi {
     }

     private void insertPhiInstr(BasicBlock basicBlock) {
-        PhiInstr phiInstr = new PhiInstr(this.allocateInstr.getTargetType(), basicBlock);
+        // 使用已找到的最大变量编号+1来分配新的变量名，确保唯一性
+        String uniqueVarName = "%v" + (this.maxVarIndex + 1);
+        this.maxVarIndex++;  // 更新最大变量编号
+
+        PhiInstr phiInstr = new PhiInstr(this.allocateInstr.getTargetType(), basicBlock, uniqueVarName);
         basicBlock.addInstruction(phiInstr, 0);
         // phi既是define，又是use
         this.useInstrs.add(phiInstr);
         this.defineInstrs.add(phiInstr);
     }

+    /**
+     * 查找函数中已使用的最大变量编号
+     * 变量名格式为 %v{数字}
+     */
+    private int findMaxVarIndex(Function function) {
+        int maxIndex = -1;
+
+        // 遍历函数中所有基本块
+        for (BasicBlock basicBlock : function.getBasicBlocks()) {
+            // 遍历基本块中所有指令
+            for (Instruction instr : basicBlock.getInstructionList()) {
+                String varName = instr.getName();
+                if (varName != null && varName.startsWith("%v")) {
+                    try {
+                        // 提取变量编号
+                        int index = Integer.parseInt(varName.substring(2));
+                        if (index > maxIndex) {
+                            maxIndex = index;
+                        }
+                    } catch (NumberFormatException e) {
+                        // 如果变量名不是%v{数字}格式，忽略
+                    }
+                }
+            }
+        }
+
+        // 也检查参数
+        for (Parameter param : function.getParameters()) {
+            String varName = param.getName();
+            if (varName != null && varName.startsWith("%v")) {
+                try {
+                    int index = Integer.parseInt(varName.substring(2));
+                    if (index > maxIndex) {
+                        maxIndex = index;
+                    }
+                } catch (NumberFormatException e) {
+                    // 忽略
+                }
+            }
+        }
+
+        return maxIndex;
+    }
+
+    @SuppressWarnings("unchecked")
     private void convertLoadStore(BasicBlock renameBlock) {
         final Stack<Value> stackCopy = (Stack<Value>) this.valueStack.clone();
         // 移除与当前allocate相关的全部的load、store指令
```

#### optimize\MemToReg.java

```
diff --git a/optimize/MemToReg.java b/optimize/MemToReg.java
index c7c43c8..d74a064 100644
--- a/optimize/MemToReg.java
+++ b/optimize/MemToReg.java
■ @@ -14,19 +14,67 @@ public class MemToReg extends Optimizer {
     public void optimize() {
         for (Function function : module.getFunctions()) {
             BasicBlock entryBlock = function.getBasicBlocks().get(0);
+            // 为函数找到已使用的最大变量编号，所有InsertPhi对象共享这个信息
+            int maxVarIndex = findMaxVarIndex(function);
             for (BasicBlock basicBlock : function.getBasicBlocks()) {
                 ArrayList<Instruction> instrList = new ArrayList<>(basicBlock.getInstructionList());
                 for (Instruction instr : instrList) {
                     if (this.isValueAllocate(instr)) {
                         InsertPhi insertPhi =
-                            new InsertPhi((AllocaInstr) instr, entryBlock);
+                            new InsertPhi((AllocaInstr) instr, entryBlock, maxVarIndex);
                         insertPhi.addPhi();
+                        // 更新最大变量编号，以便后续InsertPhi对象使用
+                        maxVarIndex = insertPhi.getMaxVarIndex();
                     }
                 }
             }
         }
     }

+    /**
+     * 查找函数中已使用的最大变量编号
+     * 变量名格式为 %v{数字}
+     */
+    private int findMaxVarIndex(Function function) {
+        int maxIndex = -1;
+
+        // 遍历函数中所有基本块
+        for (BasicBlock basicBlock : function.getBasicBlocks()) {
+            // 遍历基本块中所有指令
+            for (Instruction instr : basicBlock.getInstructionList()) {
+                String varName = instr.getName();
+                if (varName != null && varName.startsWith("%v")) {
+                    try {
+                        // 提取变量编号
+                        int index = Integer.parseInt(varName.substring(2));
+                        if (index > maxIndex) {
+                            maxIndex = index;
+                        }
+                    } catch (NumberFormatException e) {
+                        // 如果变量名不是%v{数字}格式，忽略
+                    }
+                }
+            }
+        }
+
+        // 也检查参数
+        for (midend.llvm_IR.value.Parameter param : function.getParameters()) {
+            String varName = param.getName();
+            if (varName != null && varName.startsWith("%v")) {
+                try {
+                    int index = Integer.parseInt(varName.substring(2));
+                    if (index > maxIndex) {
+                        maxIndex = index;
+                    }
+                } catch (NumberFormatException e) {
+                    // 忽略
+                }
+            }
+        }
+
+        return maxIndex;
+    }
+
     private boolean isValueAllocate(Instruction instr) {
         // 只对非数组类型添加phi
         if (instr instanceof AllocaInstr allocateInstr) {
```