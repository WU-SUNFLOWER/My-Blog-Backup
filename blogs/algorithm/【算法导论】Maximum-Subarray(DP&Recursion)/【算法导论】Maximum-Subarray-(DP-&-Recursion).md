![115044523_p0.jpg](image/648fa74213a9f297b663bac1829a5d9322a828b1e660912872c1cf4c9c494f52.image)

### 求解最大子数组问题

#### 递推解法

课本中通过「股票买卖」这个生活实际问题引出了「求解最大子数组」这个算法问题（指在一个数组中找到一个连续子数组，使得该子数组的和最大）。

稍有编程经验的同学，看到这道题目，都会很自然地按如下的思路进行思考：

想象一下，假如在数组的左侧有一个子数组正在向右生长，它的目标是尽量让自己的各项和最大。我们乐观地认为，假如让该子数组尽可能地向右生长，虽然在生长的过程中可能临时纳入了某些负数，但它仍然很有可能最终碰到一个比较大的正数，使得各项和增大。

因而当这个子数组生长到数组中的某项`ar[i]`时，我们无非就只有2种选择：
1. 将`ar[i]`纳入已有的从其左侧生长过来的子数组
2. 抛弃之前已有的子数组，从`ar[i]`开始重新计算子数组

怎么来理解这2种选择呢？

第1种情况不必多说，如果`ar[i]≥0`，那么将其纳入已有的子数组中，势必可以使得该子数组的各项和继续增大。另外，即使`ar[i]`是稍稍小于`0`的负数，正如我们刚才所说，由于子数组在后续向右生长的过程中可能会碰到比较大的正数，我们需要"*容忍*"将该负数纳入子数组而导致子数组各项之和暂时变小。

当然，这种"*容忍*"并不是无限度的。考虑这么一种情况：子数组向右生长到`ar[i]`时，其各项和就**已经是一个负数**，倘若再加`ar[i]`纳入其中，无论`ar[i]`是正是负，显然我们会得到一个各项和相比`ar[i]`**更小**的子数组。这种选择显然不如从`ar[i]`开始新开一个子数组，向右生长寻找比较大的正数来得划算。所以这时我们就需要作出第2种选择。

现在回到我们求"最大子数组"的问题上来。

诚然，上述思考都是建立在我们运用贪心思想，乐观地认为"*虽然在生长的过程中可能临时纳入了某些负数，但它仍然很有可能最终碰到一个比较大的正数，使得各项和增大*"基础上的。在实际问题中，我们能够总是好运地最终碰到"*一个比较大的正数*"吗？当然不可能！

因此，每当处理完一个`ar[i]`，无论它是正是负，无论我们作出第1种还是第2种选择，由于程序永远无法知道原数组后面元素的情况，我们必须将此时子数组的各项和先记录下来。当整个数组遍历完毕之后，我们从记录中选出最大值，就是我们希望得到的真正的"最大子数组"。

以上思路的实现代码如下：

```JavaScript
// 数组开头为占位符，不影响答案
let ar = [NaN, 13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7];
// dp[i]表示生长到ar[i]为止（包含ar[i]）的子数组的各项和
let dp = [0];  
let ans = -Infinity;
for (let i = 1; i < ar.length; ++i) {
    dp[i] = Math.max(dp[i - 1] + ar[i], ar[i]);
    if (dp[i] > ans) ans = dp[i];
}
console.log(ans);
```

利用滚动变量的代码写法如下：

```JavaScript
let ar = [13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7];
let currentSum = 0;
let ans = -Infinity;
for (let i = 0; i < ar.length; ++i) {
    currentSum = Math.max(currentSum + ar[i], ar[i]);
    if (currentSum > ans) ans = currentSum;
}
console.log(ans);
```

#### 分治解法

课本中为了演示分治思想，给出了另外一种解法。

作者认为对于一个区间为`[low, high]`的数组，设`mid = (low + high) / 2`，则其最大子数组的区间`[i, j]`无非就是以下三种情况:

- 最大子数组位于原数组的左半部分，即`low ≤ i ≤ j ≤ mid`
- 最大子数组位于原数组的右半部分，即`mid ＜ i ≤ j ≤ high`
- 最大子数组横跨原数组中点，即`low ≤ i ≤ mid < j ≤ high`

据此我们可以构造递归函数求解出原数组的最大子数组。

实现代码如下：

```JavaScript
// There we guess the range of target subarray is [i, j],
// where low ≤ i ≤ mid < j ≤ high
function FindMaxCrossingSubArray(ar, low, high) {
    let mid = (low + high) >> 1;
    // find left border
    let currentSum = 0;
    let leftMaxSum = -Infinity;
    let leftBorder;
    let i = mid;
    while (i >= low) {
        currentSum += ar[i];
        if (currentSum > leftMaxSum) {
            leftMaxSum = currentSum;
            leftBorder = i;
        }
        --i;
    }
    // find right border
    let j = mid + 1;
    let rightMaxSum = -Infinity;
    let rightBorder;
    currentSum = 0;
    while (j <= high) {
        currentSum += ar[j];
        if (currentSum > rightMaxSum) {
            rightMaxSum = currentSum;
            rightBorder = j;
        }
        ++j;
    }
    return [leftBorder, rightBorder, leftMaxSum + rightMaxSum];
}

function FindMaxSubArray(ar, low = 0, high = ar.length - 1) {
    if (low === high) {
        return [low, high, ar[low] + ar[high]]
    } else {
        let mid = (low + high) >> 1;
        let [low_left, high_left, max_left] = FindMaxSubArray(ar, low, mid);
        let [low_right, high_right, max_right] = FindMaxSubArray(ar, mid + 1, high);
        let [low_mid, high_mid, max_mid] = FindMaxCrossingSubArray(ar, low, high);
        switch (Math.max(max_left, max_right, max_mid)) {
            case max_left:
                return [low_left, high_left, max_left];
            case max_right:
                return [low_right, high_right, max_right];
            case max_mid:
                return [low_mid, high_mid, max_mid];
        }
    }
}

let ar = [13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7];
console.log(FindMaxSubArray(ar))
```

这个算法对于熟悉递归函数的同学来说，还是比较好理解的。该算法的递归式为$T(n) = 2T(n/2) + Θ(n)$，时间复杂度为$Θ(n\log n)$.

这里主要需要注意的是`FindMaxCrossingSubArray`函数计算横跨数组中点的子数组时，采取区间分别向左右两边生长的策略。这是因为横跨中点的子数组各项和取到最大值，当且仅当中点左右两侧的子数组分别取到最大值。可见两边的区间分别扩展，是绝对不会产生互相干扰的。