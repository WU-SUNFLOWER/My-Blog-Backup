
![117254901_p0.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ef9a1ef4e58843e795ec8ecaa949214c~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1118&h=1688&s=1413961&e=png&b=f8eae5)

本文主要对《算法分析与设计》课程中涉及到的*Comparison Sorting Algorithm*进行整理。

为了方便对算法进行测试，这里先编写一下测试用的代码：

```JavaScript
let ar = [];
for (let i = 0; i < 100; ++i) {
    ar.push(Math.round(Math.random() * 100));
}
let ans = Array.from(ar).sort((a, b) => a - b);
let algorithm = MergeSort;  // 这里替换成要测试的算法函数
algorithm(ar);
for (let i = 0; i < ans.length; ++i) {
    if (ar[i] !== ans[i]) {
        throw new Error("The sorting algorithm is wrong!");
    }
}
console.log("The sorting algorithm is correct!");
```

## Insertion Sort

### 代码

```JavaScript
function InsertionSort(ar) {
    let len = ar.length;
    for (let i = 1; i < len; i++) {
        let elem = ar[i];
        let j = i - 1;
        // 注意这里运用了短路保护，因此两个判断条件的顺序不可颠倒！
        while (j >= 0 && elem < ar[j]) {
            ar[j + 1] = ar[j];
            j--;
        }
        ar[j + 1] = elem;
    }
    return ar;
}
```

### 复杂度分析

首先就空间复杂度而言，Insertion Sort直接就地完成排序，除了有限个临时变量之外并不需要额外的空间。因此该算法的空间复杂度为$O(1)$.

再来看看时间复杂度。首先外层循环毋庸置疑需要迭代$n - 1$次。至于算法最核心的内层循环，我们考察最坏情况，即每次数组元素`ar[i]`都要被调往数组首元素，因此每次外层循环迭代时，内层循环的迭代次数分别为$1$、$2$、$3$、$\dots$、$n - 1$.做一个简单的数列求和，我们就知道该算法的整体时间复杂度上界为$O(n^2)$.

## Merge Sort

### 代码

朴素版本的代码如下：

```JavaScript
// 处理区间ar[low, high)
function MergeSort(ar, low = 0, high = ar.length) {
    let mid = (low + high) >> 1;
    // 递归基：仅含一个元素的区间自然有序
    if (high - low <= 1) return; 
    // 区间Left: ar[low, mid)
    MergeSort(ar, low, mid);
    // 区间Right: ar[mid, high)
    MergeSort(ar, mid, high);
    
    let posLeft = 0;
    let posRight = mid;
    let posOriginal = low;
    // 为了防止覆盖，要缓存一份区间Left
    let leftAr = ar.slice(low, mid);
    let leftLen = leftAr.length;
    while (posLeft < leftLen || posRight < high) {
        // 区间Left元素偏小
        if (posLeft < leftLen && (posRight >= high || leftAr[posLeft] <= ar[posRight])) {
            ar[posOriginal++] = leftAr[posLeft++];
        }
        // 区间Right元素偏小
        if (posRight < high && (posLeft >= leftLen || ar[posRight] < leftAr[posLeft])) {
            ar[posOriginal++] = ar[posRight++];
        }
    }
}
```

经过对该算法的分析，我们注意到当区间Left中的元素全部耗尽被写回原数组时，区间Right中位于`[posRight, high)`的元素逻辑上即全部就位，也就是说此时用于实现merge的循环就可以退出了。

因此我们可以对前述代码再作进一步精简：

```JavaScript
    // 只需要考虑区间Left元素提前耗尽的情况
    while (posLeft < leftLen) {
        // 区间Right元素偏小
        if (posRight < high && ar[posRight] < leftAr[posLeft]) {
            ar[posOriginal++] = ar[posRight++];
        }
        // 区间Left元素偏小
        if (posRight >= high || leftAr[posLeft] <= ar[posRight]) {
            ar[posOriginal++] = leftAr[posLeft++];
        }
    }
```

### 复杂度分析

Merge Sort是一个非常经典的*divide-and-conquer*算法，经过之前课程的学习，我们很容易写出它的递归式$T(n)=2T(n/2)+O(n)$.

由Master Theorem，该算法时间复杂度$T(n) = Θ(n\log n)$.

至于空间复杂度，通过树状图法，我们观察到树状图的总高度约为$\log_2 n$，且每层需要开辟的额外空间（`leftAr`）为$\frac {n} {2}$，因此该算法的空间复杂度为$O(n\log n)$.

## Heap Sort

### 代码

```JavaScript
// 堆区范围[parent, n)
function PercolateDown(ar, parent, n) {
    let lchild = 2 * parent + 1;
    let rchild = 2 * parent + 2;
    let val = ar[parent]; // 待下滤的元素
    // 不停地将元素下滤
    while (
        lchild < n && val < ar[lchild] ||
        rchild < n && val < ar[rchild]
    ) {
        // 如果左节点最大或者右节点不存在，
        // 则将其置换上来
        if (rchild >= n || ar[rchild] <= ar[lchild]) {
            ar[parent] = ar[lchild];
            parent = lchild;
        }
        // 如果右节点存在且最大，
        // 则将其置换上来
        else {
            ar[parent] = ar[rchild];
            parent = rchild;
        }
        lchild = 2 * parent + 1;
        rchild = 2 * parent + 2;
    }
    // 最后别忘了将待下滤元素放在合适的位置
    ar[parent] = val;
    // 返回被下滤元素最终所处的位置
    return parent;
}

// 处理区间ar[low, high)
function HeapSort(ar) {
    let n = ar.length;
    /* 自下而上，自右向左下滤构建大顶堆 */
    let innerNode = Math.floor(n / 2) - 1;
    while (innerNode >= 0) {
        PercolateDown(ar, innerNode, n);
        // 准备下滤二叉树中同层的左侧元素
        --innerNode;
    }
    
    /* 实现堆排序 */
    // 堆区范围[0, high)
    let high = n;
    while (high > 1) {
        // 将堆顶的最大元素调入数组末尾
        // 并将堆的规模缩减1
        let tailElem = ar[high - 1];
        ar[high - 1] = ar[0];
        ar[0] = tailElem;
        // 将从堆底调入堆顶的元素重新下滤
        PercolateDown(ar, 0, --high);
    }
}
```

### 复杂度分析

通过阅读代码我们发现，这个算法分为两大部分，即"建堆"和"堆排序"。

我们先来分析一下"建堆"的时间开销。

由于所有的非叶子节点（即代码中的`innerNode`，共$\frac {n} {2}个$）都要进行下滤操作，且最坏情况下这些节点都要被下滤到完全二叉树的最底层。此外我们注意到，最坏情况下节点下滤的路径长度与其位于二叉树的层数成反比。也就是说对于越高的层数（即二叉树中越靠下的层），这一层的节点越多，而它们最坏情况下下滤的路径恰好越短。反过来，如果层数越低（即二叉树中越靠上的层），这一层的节点越少，它们最坏情况下下滤的路径恰好要更长一些。从直觉上讲，这个算法实现了"节点数量"和"下滤路径长度"之间的平衡，我们有理由相信它的时间复杂度应当是比较好的。

下面我们通过具体的数学推导来验证我们的直觉。

除去全为叶子节点的最后一层，我们假设剩余层中的所有非叶子节点都要被下滤。若记$t = \lfloor \log_2 {n} \rfloor$，则最坏情况下所有非叶子节点的下滤操作次数为$T(n) = \sum\limits_{i=1}^{t - 1} {2^i(t - i)}$

由高中数学，可推知$T(n) = 2^{\lfloor \log_2 n \rfloor+1}-2\lfloor \log_2 {n} \rfloor - 2 = O(n)$. 

也就是说最坏在线性时间内我们就能完成建堆操作，这看上去还是蛮不错的。

接下来我们分析"堆排序"操作的时间复杂度。

我们依然按每次迭代时堆顶元素都要下滤至堆底的最坏情况分析。

由Stirling近似公式，$\log{(n)} + \log{(n-1)} + \dots + \log{(1)} = O( \log({\sqrt{n}n^n)} ) = O(n\log n)$.

综上所述，Heap Sort的时间复杂度上界为$O(n\log n)$.

至于空间复杂度，该算法只需借助有限个必须的变量即可实现对原数组的就地排序，因此其空间复杂度为$O(1)$.

## Quick Sort

为了编码方便起见，我们取区间中的首个元素作为`pivot`。

### 代码

**版本一：**

```JavaScript
// 处理区间ar[low, high)
function QuickSort(ar, low = 0, high = ar.length) {
    let pivot = ar[low];
    let i = low;
    let j = high - 1;
    if (high - low <= 1) return;  // 递归基
    while (i < j) {
        // 此时ar[i]逻辑上为空
        // 需要寻找一个合适的ar[j]调上来
        while (i < j && ar[j] >= pivot) --j;
        ar[i] = ar[j];
        // 此时ar[j]逻辑上为空
        // 需要寻找一个合适的ar[i]调上来
        while (i < j && ar[i] <= pivot) ++i;
        ar[j] = ar[i];
    }
    // 此时ar[i]或ar[j]逻辑上为空
    // 可以放心地调入pivot
    ar[i] = pivot;
    // 分治
    QuickSort(ar, low, i);
    QuickSort(ar, i + 1, high);
}
```

**版本二：**

这是一个快排的变种版本，在《Introduction to Algorithms》和THU邓俊辉教授的网课里均有介绍。本人印象中某个早期版本的V8引擎中也使用了类似的快排实现。

其主要思路为将数组区间划分为四个部分：`[low] ∪ Less(low, i] ∪ Greater[i+1, j) ∪ Unknown[j, high)`，再通过不断从区间Unknown中抽取元素并与`pivot`比较的方式，实现对原数组区间的分块。

```JavaScript
// 处理区间ar[low, high)
function QuickSort(ar, low = 0, high = ar.length) {
    let pivot = ar[low];
    let i = low;
    let j = low + 1;
    // 别忘了递归基
    if (high - low <= 1) return;
    // 不断消耗Unknown中的元素
    while (j < high) {
        // 第一种情况：如果ar[j]<pivot
        // 将ar[j]调入Less，exchange ar[i+1], ar[j]
        // 最后别忘了将区间Less向右生长一个单位
        if (ar[j] < pivot) {
            let t = ar[j];
            ar[j] = ar[++i];
            ar[i] = t;
        }
        // 第二种情况：如果ar[j]≥pivot
        // 区间Greater左区间向右收缩一个单位，此外啥也不做
        ++j;
    }
    // 此时Unknown区间为空，将pivot调入Less和Greater的边界处
    ar[low] = ar[i];
    ar[i] = pivot;
    // 分治
    QuickSort(ar, low, i);
    QuickSort(ar, i + 1, high);
}
```

### 复杂度分析

#### 时间复杂度

我们先来看最坏情况下的时间复杂度。在最坏情况下，每一次子问题的规模都缩减一个元素，即$T(n) = T(n - 1) + Θ(n)$.

由代入法可知，最坏情况下$T(n) = Θ(n^2)$.

再来看最好情况。在最好情况下，每次问题的规模都被顺利地分解为了原问题的二分之一，即$T(n) = 2T(n/2) + Θ(n)$.

由Master Theorem可知，最好情况下$T(n) = Θ(n \log n)$.

好消息是，通过严谨的数学证明可知，在随机输入原数组的情况下，快排的期望时间复杂度仍为$O(n \log n)$.

（这个比较复杂，先占个位，以后有机会再补充qwq）

#### 空间复杂度

很显然，与Heap Sort类似，该算法只需借助有限个必须的变量即可实现对原数组的就地排序，因此其空间复杂度为$O(1)$.

## 比较排序算法下界定理

从前面列举的三种排序算法中，我们发现它们的渐进时间复杂度都是$O(n\log n)$这个级别的。事实上这不是巧合，正如《*Introduction to Algorithms*》中指出的那样——**在最坏情况下，任何Comparison Sort Algorithm都需要做$Ω(n\log n)$次比较。**

此定理的证明在书中已经通过数学式子进行了非常严谨的阐述，这里我仅提炼其中比较关键的思维过程：

1. 无论一个Comparison Sorting Algorithm的具体运行过程如何，想要最终想要将有限长度的原序列变成有序的已排序序列，在数学底层上都依赖于在算法运行过程中执行有限次的比较。
2. 为什么算法通过执行有限次的比较，就能得到有序序列呢？这是因为每执行一次比较，我们就可以确定原序列中任意两个元素的偏序关系。显然，最坏情况下，我们需要知道原序列中任意的两个元素之间的偏序关系，才可以确定对原序列排序之后的结果是什么。
3. 为了定量分析所谓"最坏情况"下我们需要执行的比较次数，我们引入了决策树。且由于我们将序列中任意两元素的比较结果简化为`≤`和`>`两类，决策树的非叶子节点有且只有两个分叉。
4. 决策树的每个叶子节点都表示一种可能的排序结果，因此决策树中应当有$n!$个叶子节点。
5. **从决策树根节点出发，抵达某一个叶子节点（即算法得到有序序列）的过程中，都可以映射为排序算法对原序列中的某两个数之间进行比较，最终得出有序序列的过程。**
6. 设二叉决策树的高度为$h$（这也是排序算法要进行的比较次数的infimum），则有$2^h ≥ n!$，即$h ≥ \log (n!) = Ω(n\log n)$.
7. 在真实的排序算法实现中，经常不可避免地会发生一些其余的、位于决策树讨论范畴之外的比较，因此$Ω(n\log n)$已是比较排序算法理论上所能触及的下确界了。
