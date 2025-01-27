
![id=54763430.jpg](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1c0fb7111d1948e39b9cf2238aecfa98~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=800&h=1150&s=327649&e=jpg&b=fafaee)

# Minimum and maximum

在某些实际问题中，我们需要同时从某个数组中找出最小值和最大值。朴素的方法是我们可以编写两个循环，分别找出最小值和最大值——这将花费$(n - 1) + (n - 1) = 2n-2$次比较。

下面给出一种快速的同时寻找最大值和最小值算法。

```javascript
function findMinAndMax(ar) {
    let len = ar.length;
    let i, min, max;
    
    // 针对数组长度的奇偶情况初始化临时变量
    // 注意：在分析算法时，我们忽略这里的if condition带来的比较开销！
    if (ar.length % 2 == 0) {
        i = 2;
        ar[0] > ar[1] ? 
            (max = ar[0], min = ar[1]) : 
            (max = ar[1], min = ar[0])
    } else {
        i = 1, min = ar[0], max = ar[0];
    }
    
    while (i < len) {
        let a = ar[i];
        let b = ar[i + 1];
        let t_min, t_max;
        
        // 先比较a、b
        a > b ? (t_min = b, t_max = a) : (t_min = a, t_max = b);
        // 比较确定是否更新最小值
        if (t_min < min) min = t_min;
        // 比较确定是否更新最大值
        if (t_max > max) max = t_max;
        
        i += 2;
    }
    return [min, max];
}
```

当数组的长度为偶数时，这个算法共要在数组元素间执行$1 + (n-2) /2 × 3 = 3n/2-2$次比较. 当数组长度为奇数时，这个算法共要执行$(n-1)/2×3 = 3n/2 - 3/2$次比较. 可见这个算法相比于朴素算法在性能上确实有了提升。

# Top-K问题

"顺序统计量"问题中还有一个很经典的问题，即Top-K问题。这个问题要求我们设计算法，从一个比较长的数组中，尽可能快速地查找出在所有数组元素中位居前$k$大的元素（$k=1, 2, \dots, n$）.

这里为了方便，我们规定用户输入的数组中没有重复的元素。

## $O(n^2)$法

一种简单的方案是，我们借用经典的排序算法模板(选择排序、冒泡排序等)来实现对目标元素的就地查找。

一种可能的实现如下：

```JavaScript
function TopK(ar, k) {
    let len = ar.length;
    for (let i = 0; i < k; i++) {
        let idx = i;
        for (let j = i + 1; j < len; j++) {
            if (ar[j] > ar[idx]) {
                idx = j;
            }
        }
        let t = ar[i];
        ar[i] = ar[idx];
        ar[idx] = t;
    }
    // 当循环结束后，区间[0, k)即为原数组中的第1大~第k大元素
    return ar.slice(0, k);
}
```

很轻松地，我们知道该算法中最核心的比较操作在$k$次外循环迭代中，其执行次数分别为$n-1$、$n-2$、$\dots$、$n-k$. 求累加和，我们知道该算法的时间复杂度为$O(nk)$.

然而，在$k → n$的最坏情况下，该算法的渐进复杂度将达到不甚理想的$O(n^2)$，我们需要探索更好的解决方案。

## Heap法

我们也可以借助最小堆，通过不断对最小堆中相对于整个原数组较小的元素进行替换的手法，来解决Top-K问题。

```JavaScript
// 维护小顶堆——堆元素下滤操作
// 堆的区间为[0, n)
function PercolateDown(ar, parent, n) {
    let val = ar[parent];
    let lchild = parent * 2 + 1;
    let rchild = parent * 2 + 2;
    while (
        lchild < n && ar[lchild] < ar[parent] ||
        rchild < n && ar[rchild] < ar[parent]
    ) {
        // 如果右节点不存在，或者左节点最小，则将左节点换上来
        if (rchild >= n || ar[lchild] < ar[rchild]) {
            ar[parent] = ar[lchild];
            parent = lchild;
        }
        // 如果不是前面的这两种情况，那么说明右节点存在且最小
        else {
            ar[parent] = ar[rchild];
            parent = rchild;
        }
        lchild = parent * 2 + 1;
        rchild = parent * 2 + 2;
    }
    // 最后别忘了放置要下滤元素的值
    ar[parent] = val;
}

function TopK(ar, k) {
    // 在区间[0, k)上就地建立一个大顶堆
    // 就地建堆方向：自右向左
    let innerNode = Math.floor(k / 2) - 1;
    while (innerNode >= 0) {
        PercolateDown(ar, innerNode, k);
        innerNode--;
    }
    // 遍历[k, length)上的元素
    // 若该区间中的元素比堆顶元素大
    // 则用该元素替换堆顶元素，再更新一次堆
    for (let i = k; i < ar.length; i++) {
        if (ar[i] > ar[0]) {
            ar[0] = ar[i];
            PercolateDown(ar, 0, k);
        }
    }
    // 当循环结束后，区间[0, k)即为原数组中的第1大~第k大元素
    return ar.slice(0, k);
}
```

由关于二叉堆的知识，在这个算法中建堆需要消耗时间$O(k)$. 在后续的循环中，最坏情况下堆顶元素要被下滤$n - k + 1$次，每次下滤的时间开销为$O(\log_2 k)$. 因此该算法的时间复杂度上界为$O(n \log_2 k)$. 而一般在实际问题中$k >> 2$，因此该算法的效率虽然相比Select法有所提升，但仍不能达到线性时间. 

## QuickSelect法

### 算法基本思想

从快排的理解角度来看，QuickSelect运行时，首先在原数组中任选一个元素作为`pivot`，再将原数组`ar`划分成`ar[0~i-1]>pivot`、`ar[i]==pivot`、`ar[i+1~length-1]<pivot`这三段段。当然仅仅依靠这种理解方法，对于解决Top-K问题还是有点棘手的。现在让我们来换个理解的角度。

从Top-K问题的角度来看，我们也可以认为每次迭代后数组会被划分为两段：`ar[0~i-1]`——由原数组中第`1`大\~第`i`大元素组成的集合，`ar[i~n)`——由原数组中第`i+1`大\~第`n`大元素组成的集合。因此我们可以直接根据`i`与`k`的关系，来决定下一次迭代时区间`ar[low, high]`的范围如何调整。直至`i==k`，即区间`ar[0~i-1]`恰好为第`1`大~第`k`大元素所组成的区间时，我们退出迭代。

### 代码实现

QuickSelect算法的实现与QuickSort十分类似，主要难点在于**正确处理各种边界条件**，以及**正确理解数组某处"逻辑为空"的概念**。对这些问题的处理具体请见注释。

此外，这里为了方便代码演示，我直接在每次循环迭代时选取第`0`个元素作为`pivot`.

```JavaScript
function TopK(ar, k) {
    // low和high用以维护处理数组的区间范围
    let low = 0;
    let high = ar.length - 1;
    // 外层循环保证数组划分可以不断进行，数组区间可以不断被缩小
    while (low < high) {
        let i = low;
        let j = high;
        // 随机选取pivot并在逻辑上将其抽出数组
        // 并将ar[i]调入填充此位置
        // 经过此操作，ar[i]在逻辑上为空
        let randomPos = low + Math.floor(Math.random() * (high - low + 1));
        let pivot = ar[randomPos];
        ar[randomPos] = ar[i];
        // 内层循环控制单次数组划分进行
        // 这里不能取i <= j，是因为要预留一个逻辑上的空位
        // 方便一轮数组划分结束后，能够正确放置pivot
        while (i < j) {
            // 此时数组左侧ar[i]处逻辑上为空，
            // 我们要找一个ar[j]>pivot填充这个空位
            while (i < j && ar[j] <= pivot) --j;
            // 这里要注意即使i和j指针已经相遇
            // 这条代码也不会引发错误（妙！）
            ar[i] = ar[j];
            // 此时数组右侧ar[j]处逻辑上为空
            // 我们要找一个ar[i]<pivot填充这个空位
            while (i < j && ar[i] >= pivot) ++i;
            ar[j] = ar[i];
        }
        // 当i、j指针相遇时，此时必有ar[i]或ar[j]逻辑上为空
        // 因此我们可以放心地将pivot放置于此处
        ar[i] = pivot;
        /*
            此时数组被分为了两段，
            ar[0~i-1]——包括第1大~第i大元素
            ar[i~n-1]——第i+1大~第n大元素
        
            当k == i时，说明区间ar[0~i-1]中恰好包括有第1大~第k大元素
            
            当k < i时，说明第1大~第k大元素是区间ar[0~i-1]的一个子集
            
            当i < k时，区间ar[0~i-1]还没包括第1大~第k大的所有元素
            剩余的元素还需要到区间ar[i, high]中寻找
        */
        if (k < i) high = i - 1;
        else if (i < k) low = i;
        else break;
    }
    return ar.slice(0, k);
}
```

### 性能分析

我们注意到，QuickSelect算法的内循环需要线性时间$O(n)$完成，而通过数学证明可知外层循环在平均情况下可以保证在执行有限常数次后结束。但在极端情况（原数组已按升序排序，且每次恰好选取区间中的第一个元素作为`pivot`）下，仍要执行$O(n)$次。

因此该算法平均时间复杂度可达$O(n)$，最坏情况时间复杂度复杂度$O(n^2)$. 可见在平均情况下，该算法的时间复杂度为线性且完全不依赖于$k$，性能是相当优异的.

## LinearSelect法

