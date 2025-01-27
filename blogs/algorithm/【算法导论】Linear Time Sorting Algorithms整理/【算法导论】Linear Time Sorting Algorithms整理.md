
![109715099_p0.jpg](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/41b019b47c7945f985326fe4aa420fe5~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=4320&h=2160&s=550434&e=jpg&b=e2dbaf)

书接上回[【专业课学习】Comparison Sorting Algorithm整理](https://juejin.cn/user/3544481220008744/posts)，这次我们来看看依赖额外空间的*Linear Time Sorting Algorithm*。

# Counting Sort

## 代码

```JavaScript
// maxNumber表示待排序数组中可能出现的元素最大者
// 为了方便，我们假设待排序数组中元素的最小值为0
function CountSort(ar, maxNumber) {
    let count = new Array(maxNumber + 1).fill(0);
    // 元素计数
    for (let i = 0; i < ar.length; ++i) {
        ++count[ar[i]];
    }
    // 求前缀和
    for (let i = 1; i <= maxNumber; ++i) {
        count[i] += count[i - 1];
    }
    // 为了保证算法stable，
    // 从后向前放置原数组中的元素
    let ret = new Array(ar.length);
    for (let i = ar.length - 1; i >= 0; --i) {
        ret[count[ar[i]] - 1] = ar[i];
        --count[ar[i]];
    }
    return ret;
}
```

## 复杂度分析

我们先来看看该算法的时间复杂度。该算法中有三个for循环，它们的耗时分别为$Θ(n)$、$Θ(maxNumber)$、$Θ(n)$，因此算法的总耗时应为$Θ(2n + maxNumber)$。在实际工作中，我们通常更容易遇到$n >> maxNumber$的情形，这时我们可以认为该算法的渐进时间复杂度就是$Θ(n)$.

至于空间复杂度方面，我们知道该算法需要额外$O(maxNumber)$的空间进行计数。可见该算法在节省空间开销方面是不如Quick Sort等就地排序算法的。

# Radix Sort

## 代码

```JavaScript
function StableSort(ar, ret, keyDigit) {
    let maxNumber = 10;
    let count = new Array(maxNumber + 1).fill(0);
    // 用来提取某个整数中指定位的数值
    const getDigitNumber = (n, digit) => Math.floor(n / 10 ** (digit - 1)) % 10;
    for (let i = 0; i < ar.length; ++i) {
        ++count[getDigitNumber(ar[i], keyDigit)];
    }
    for (let i = 1; i <= maxNumber; ++i) {
        count[i] += count[i - 1];
    }
    for (let i = ar.length - 1; i >= 0; --i) {
        let digit = getDigitNumber(ar[i], keyDigit);
        ret[count[digit] - 1] = ar[i];
        --count[digit];
    }
    return ret;
}

function RadixSort(ar, highestDigit) {
    let temp = [];
    for (let i = 1; i <= highestDigit; ++i) {
        /* 
           当次排序中ar作为输入数组
           temp作为缓存临时结果的数组

           在下一轮排序时再将temp作为输入数组，
           此时ar在逻辑上为空，
           可用作储存下一轮排序的临时结果。
           
           二者循环往复，直到循环迭代结束。
           退出循环时最终结果就储存在ar中。
        */
        StableSort(ar, temp, i);
        [ar, temp] = [temp, ar];
    }
    return ar;
}

RadixSort([329, 457, 657, 839, 436, 720, 355], 3);
```

## 正确性证明

正如《*Introduction to Algorithms*》中所说的那样，我们很容易对Radix Sort从十进制数从低位向高位逐位迭代排序产生困惑，因为这与我们直观感受的"从高位向低位逐位迭代排序"相悖。那么为什么Radix Sort的结果一定是正确的呢？

我们可以用数学归纳法做一个简单的推理。

为了方便，我们首先规定数组中各十进制整数元素的最左边一位（最低位）为第$1$位，位数自右向左增大。

首先，算法会根据各元素第$1$位对数组进行排序。

再之，当算法准备根据数组中元素的第$i$位（$i > 1$）进行排序时，我们假设数组中各元素仅就第$1$位到第$i-1$位而言已经有序。于是在算法完成根据根据各元素第$i$位数值的排序后，对于数组中的任意两个元素$a, b$而言，无非会出现如下两种情况：

- 元素$a$的第$i$位和$b$的第$i$位不同，则经过当次排序后，对于$a, b$元素的第$1$位到第$i$而言，它们在数组中的位置一定已有序排列。
- 元素$a$的第$i$位和$b$的第$i$位相同，则当次排序后它们在元素中的位置，应由它们的第$1$位到第$i-1$位决定。由于我们在迭代过程中采用稳定的排序算法，我们一定能够做到这一点，从而保证了对于$a, b$元素的第$1$位到第$i$而言，它们在数组中的位置一定已有序排列。

可见，当算法完成根据元素第$i$位数值对数组的排序后，就数组中各个元素的第$1$位到$i-1$位而言，它们的顺序一定是有序的。算法就会这样一直迭代，直到最后得到正确的结果。

## 复杂度分析

我们很容易注意到Radix Sort的时间复杂度与实现该算法时内部采用的Stable Sort算法的时间复杂度直接相关。就本人在前面示例代码中采用Counting Sort进行实现而言，此时Radix Sort的时间复杂度就是$Θ(highestDigit × n)$.

至于空间复杂度，仅就本人的示例代码而言，我们很遗憾地看到，Radix Sort需要花费额外的$O(n)$空间储存排序过程中产生的中间结果，在节约空间开销的方面仍然是远不及就地排序算法的。