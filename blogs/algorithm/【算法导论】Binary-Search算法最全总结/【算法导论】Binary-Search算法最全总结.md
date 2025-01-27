
![86247816_p0.jpg](image/65ca8abcabaaf8bf491ff3e9273888e9f9c42e47c41cef7ebc3d9a8e329cbae8.image)

BinarySearch是同学们耳熟能详的一种用于已排序顺序表的查找算法，也是很多同学最早接触的*decrease-and-conquer*算法。

但实际上在编程实现BinarySearch的过程中，**对边界条件的处理却是非常容易犯错的地方**，稍有不慎便有可能写出错误的代码。本文就对这个问题进行一些简要的探讨。

### 版本A

首先，我们先来看一下最简单的BinarySearch实现。这里我们规定若在原数组中查找不到目标元素，则返回`-1`。

```JavaScript
function BinarySearch(ar, target) {
    let low = 0;
    let high = ar.length;
    // 维护查找区间[low, high)
    while (low < high) {
        let mid = (low + high) >> 1;
        // 查找目标在右半边，将查找区间调整为[mid + 1, high)
        if (ar[mid] < target) {
            low = mid + 1;
        }
        // 查找目标在左半边，将查找区间调整为[low, mid)
        else if (target < ar[mid]) {
            high = mid;
        }
        else {
            return mid;
        }
    }
    return -1;
}
```

### 版本B

#### 算法思路

审视上一个版本A，我们发现了一个比较尴尬的事情：为了区分`ar[mid]`大于、小于、等于`target`这三种不同的情况，我们不得不在每次查找循环迭代时，编写两个conditions。这就导致在理论上，每次迭代时若想要向右侧继续查找元素，比较次数总是大于向左侧继续查找。

对此，我们可以编写出如下版本的BinarySearch：

```JavaScript
function BinarySearch(ar, target) {
    let low = 0;
    let high = ar.length;
    // 维护查找区间[low, high)
    while (high - low > 1) {
        let mid = (low + high) >> 1;
        // 查找目标在右半边，将查找区间调整为[mid, high)
        if (ar[mid] <= target) {
            low = mid;
        }
        // 查找目标在左半边，将查找区间调整为[low, mid)
        else {
            high = mid;
        }
    }
    // 当high == low + 1时，此时区间变为[low, low + 1)
    // 即区间中只有元素ar[low]
    // 这时再判断一下ar[low]与target是否相等
    return ar[low] === target ? low : -1;
}
```

这段代码的基本思路在于，为了将每次循环迭代时condition的数量削减到一个，我们在整个循环迭代的过程中始终不去显示地判断`ar[mid]`是否等于`target`；只要`ar[mid] ≤ target`，我们就将`mid`视作下一次循环迭代的左边界`low`。最后，当循环退出时，区间`[low, high)`的长度必然已经缩小为1，此时检查`ar[low]`是否与`target`相等即可。

#### 正确性分析

那么这个算法是否是正确的呢？我们可以从它的**单调性**和**不变性**入手分析。

首先就单调性而言，我们需要分析该算法是否能保证循环迭代期间区间$[low, high)$始终在缩小，以确保迭代循环能正确退出。

不妨设$high = low + k$，根据循环条件有$k > 1$，即$k ≥ 2$.

于是$mid = \frac{\lfloor {low + high} \rfloor}{2} = \lfloor {low + \frac{k}{2}} \rfloor$

于是$low < low + 1 ≤ mid ≤ low + \frac{k}{2} < high$

可见该算法能够保证在循环迭代期间，严格地有$low < mid < high$，于是无论在本次迭代中算法选择执行$low = mid$还是$high = mid$，都能确保查找区间在不断缩小并最终退出循环。

接下来我们考察算法的不变性，这关系到迭代算法最终是否能得出正确的结果。

通过观察算法实现代码，我们发现该算法在每次迭代的过程中，似乎始终能将数组划分为三个含义不同的区间：

- 左区间$\left[ 0, low \right)$，对其中的任意元素$ar\left[0, low\right)$都有$ar\left[0, low\right) ≤ target$.
- 未定区间$\left[low, high\right)$，这是算法运行到此刻正准备进行进一步划分的子区间，其中的元素与$target$之间的大小关系不确定。
- 右区间$\left[high, length \right)$，对其中的任意元素都有$target < ar\left[high, length\right)$

我们通过数学归纳法来验证我们的观察假设。

- 当算法启动时，$low=0, high=length$，左右区间都为$\varnothing$，任何命题对于空集都成立.
- 在某次算法准备根据新计算出来的$mid$更新待迭代区间时，无非就只有两种情况：
- - 若$ar\left[mid\right] ≤ target$，左区间更新为$\left[0, mid\right)$. 由原序列的单调性知，新的左区间中的任意元素仍然小于等于$target$.
- - 若$target < ar\left[mid\right]$，右区间更新为$\left[mid, length\right)$，同样地，我们发现新的右区间中的任意元素仍然大于$target$.



最后，让我们来看看算法运行结束时的情况。当不定区间$\left[low, high\right)$的长度缩短为1时，区间中仅剩的元素即为$ar\left[low\right]$。对于该元素左侧的所有元素，由于落在左区间，它们都小于等于$target$；而对于该元素右侧的所有元素，由于落在右区间，它们都大于$target$. 又由于数组$ar$的单调有序性，我们可以知道对于$ar\left[low\right]$，它很有可能恰好等于$target$，不过也可能大于或者小于$target$，我们只需要在最后做一次判断即可。

可见该算法的不变性是能够得到保证的，通过该算法我们能得到正确的结果。

#### 避坑提示

这个思路看上去的确很精巧，但是如果自己写代码实现这个思路，稍有不慎，我们就很容易写出如下的**错误代码**：

```JavaScript
function BinarySearch(ar, target) {
    let low = 0;
    let high = ar.length;
    // 维护查找区间[low, high)
    while (high - low > 1) {
        let mid = (low + high) >> 1;
        // 查找目标在右半边，将查找区间调整为[mid + 1, high)
        if (ar[mid] < target) {
            low = mid + 1;
        }
        // 查找目标在左半边，由于target可能含在左半边
        // 将查找区间调整为[low, mid+1)，即[low, mid]
        else {
            high = mid + 1;
        }
    }
    return ar[low] === target ? low : -1;
}
```

分析这段代码，我们发现不同于前述的代码，这里采用将$ar\left[mid\right] ≥ target$并入左区间的处理方式。虽然这看似没有问题，但实际上这么处理是无法保证算法单调性的。

具体来说，当$ar\left[mid\right] ≥ target$时，这段代码执行更新操作$high_{new} = mid + 1 = low + \lfloor {\frac k 2}\rfloor + 1$. 这时若恰有$k = 2$，就有$high_{new} = high_{old} = mid + k$. 也就是说迭代区间并没有发生任何减小，这会导致程序死循环！

### 版本C

在前面的两个版本中，我们规定倘若找不到目标元素就直接返回`-1`。现在我们变更一下需求，要求将我们的算法能够返回数组中不大于$target$的最后一个元素的下标：

- 例如对于`ar=[1, 2, 3, 3, 3, 4, 5, 6]`和`target=3`，我们希望得到下标`4`.
- 又如对于`ar=[1,2,4,6]`和`target=5`，我们希望得到下标`2`
- 再如对于`ar=[1, 2, 3]`和`target=4`，我们希望得到下标`2`

另外地，我们规定：
- 例如对于`ar=[1, 2, 3]`和`target=0`，我们希望能够得到下标`-1`（即假想在`ar[-1]`处有一个哨兵元素`-∞`）

这个问题也具备十分重要的现实意义。例如在一个升序数组中插入一个新元素时，我们希望选取一个合适的插入位置，以保证插入新元素后数组仍然有序。

算法的实现代码如下：

```JavaScript
function BinarySearch(ar, target) {
    let low = 0;
    let high = ar.length;
    // 维护查找区间[low, high)
    while (low < high) {
        let mid = (low + high) >> 1;
        // 查找目标在右半边，将查找区间调整为(mid, high)
        if (ar[mid] <= target) {
            low = mid + 1;
        } 
        // 查找目标在左半边，将查找区间调整为[low, mid)
        else {
            high = mid;
        }
    }
    return --low;
}
```

这个代码比较让人感到疑惑的地方在于，在每次迭代中得到的新未定区间$\left[mid + 1, {high}_{old}\right)$或$\left[low_{old}, mid\right)$中竟然始终不包括可能等于$target$的$ar\left[mid\right]$.

但事实上，这并不会影响算法的单调性和不变性（证明方法同版本B），并且保证了算法最后能够正确退出。

随着不定区间的不断缩小，我们很容易证明$low$和$high$指针最终一定会发生重合，并且这时它们将恰好指向右区间的首个元素（即整个数组中第一个严格大于$target$的元素）。又有整个数组的有序性，此时的$ar\left[low - 1\right]$即为我们所求的数组中最后一个不大于$target$的元素。

这个算法确实可以实现我们的需求。