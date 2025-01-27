
![47139274_p0.jpg](image/782a12a8e68a0d0c6805a6329a19a1d10a9478bf7ab2eddba32ec073e613057f.image)

有关图的算法请移步

# Dynamic Programming

##  0-1 Knapsack Problem

Recursion:

1. When `weight[i] > w`, we have `dp[i][w] = dp[i - 1][w]`.
2. When `weight[i] <= w`, we have `dp[i][w] = max{dp[i - 1][w - weight[i]] + values[i], dp[i - 1][w]}`

```javascript
function solve(n, W, weights, values) {
    let dp = [];
    // initialize
    for (let i = 0; i <= n; ++i) {
        dp[i] = [0];
    }
    for (let w = 0; w <= W; ++w) {
        dp[0][w] = 0;
    }
    // complete dp
    for (let i = 1; i <= n; ++i) {
        for (let w = 0; w <= W; ++w) {
            if (w < weights[i]) {
                dp[i][w] = dp[i - 1][w];
            } else {
                dp[i][w] = Math.max(dp[i - 1][w - weights[i]] + values[i], dp[i - 1][w]);
            }
        }
    }
    return dp[n][W];
}

// For convenience, we use values[0] and weights[0] as placeholders.
console.log(solve(8, 200, [-1, 79, 58, 86, 11, 28, 62, 15, 68], [-1, 83, 14, 54, 79, 72, 52, 48, 62]));
```

We notice that when we compute `dp[i][j]`, at most we need to know `dp[i - 1][w]` and `dp[i - 1][w - weights[i]]`, which are on the left and upper-left side relative to `dp[i][w]` in the matrix. Since that it's obvious that we can switch the order of the two-layers loop in our code.

```JAVASCRIPT
function solve(n, W, weights, values) {
    let dp = [];
    // initialize
    for (let i = 0; i <= n; ++i) {
        dp[i] = [0];
    }
    for (let w = 0; w <= W; ++w) {
        dp[0][w] = 0;
    }
    // complete dp
    for (let w = 0; w <= W; ++w) {
        for (let i = 1; i <= n; ++i) {
            if (w < weights[i]) {
                dp[i][w] = dp[i - 1][w];
            } else {
                dp[i][w] = Math.max(dp[i - 1][w - weights[i]] + values[i], dp[i - 1][w]);
            }
        }
    }
    return dp[n][W];
}

// For convenience, we use values[0] and weights[0] as placeholders.
console.log(solve(8, 200, [-1, 79, 58, 86, 11, 28, 62, 15, 68], [-1, 83, 14, 54, 79, 72, 52, 48, 62]));
```

## Longest common subsequence

Recursion：

1. When `i=0`or `j=0`，we have `dp[i][j]=0`
2. When`i>0`,`j>0`,`str1[i]==str2[j]`, we have `dp[i][j]=dp[i-1][j-1]+1`
3. When`i>0`, `j>0`, `str1[i]!=str2[j]`, we have`dp[i][j]=max{dp[i-1][j], dp[i][j-1]}`

### Find a answer

```JavaScript
function solve(str1, str2) {
    let dp = [];
    let status = [];
    // initialize
    for (let i = 0; i <= str1.length; ++i) {
        dp[i] = [0];
        status[i] = [];
    }
    for (let j = 0; j <= str2.length; ++j) {
        dp[0][j] = 0;
    }
    // complete dp and status
    for (let i = 1; i <= str1.length; ++i) {
        for (let j = 1; j <= str2.length; ++j) {
            if (str1[i - 1] == str2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
                status[i][j] = '↖';
            } 
            else if (dp[i - 1][j] >= dp[i][j - 1]) {
                dp[i][j] = dp[i - 1][j];
                status[i][j] = '←';
            }
            else {
                dp[i][j] = dp[i][j - 1];
                status[i][j] = '↑';
            }
        }
    }
    // rebuild the lcs
    let i = str1.length;
    let j = str2.length;
    let ans = [];
    while (i > 0 && j > 0) {
        switch (status[i][j]) {
            case '↖':
                ans.push(str1[i - 1]);
                --i, --j;
                break;
            case '←':
                --i;
                break;
            case '↑':
                --j;
                break;
        }
    }
    return ans.reverse().join('');
}
console.log(solve("ABCBDAB", "BDCABA"));
```

### Find all answers

```javascript
function rebuild(str1, i, j, status) {
    if (i <= 0 || j <= 0) {
        return [''];
    }
    switch (status[i][j]) {
        case '↖':
            /*
                For example, now str1[i-1]='d',
                and we get ['ab', 'ba', 'ac'] after call `rebuild(str1, i - 1, j - 1, status)`.
                Then we want to return ['abd', 'bad', 'acd'] here.
            */
            return rebuild(str1, i - 1, j - 1, status).map(s => s + str1[i - 1]);
        case '←':
            return rebuild(str1, i - 1, j, status);
        case '↑':
            return rebuild(str1, i, j - 1, status);
        case '×':
            /*
                For example, now we get ['ab'] after call `rebuild(str1, i - 1, j, status)`,
                and ['ad', 'bc'] after call `rebuild(str1, i, j - 1, status)`.
                Then we want to return ['ab', 'ad', 'bc'] here.
            */
            return [...rebuild(str1, i - 1, j, status), ...rebuild(str1, i, j - 1, status)];
    }
}

function solve(str1, str2) {
    let dp = [];
    let status = [];
    // initialize
    for (let i = 0; i <= str1.length; ++i) {
        dp[i] = [0];
        status[i] = [];
    }
    for (let j = 0; j <= str2.length; ++j) {
        dp[0][j] = 0;
    }
    // complete dp and status
    for (let i = 1; i <= str1.length; ++i) {
        for (let j = 1; j <= str2.length; ++j) {
            if (str1[i - 1] == str2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
                status[i][j] = '↖';
            }
            else if (dp[i - 1][j] == dp[i][j - 1]) {
                dp[i][j] = dp[i - 1][j];
                status[i][j] = '×';
            }
            else if (dp[i - 1][j] > dp[i][j - 1]) {
                dp[i][j] = dp[i - 1][j];
                status[i][j] = '←';
            }
            else {
                dp[i][j] = dp[i][j - 1];
                status[i][j] = '↑';
            }
        }
    }
    // rebuild the lcs
    return rebuild(str1, str1.length, str2.length, status);
}
console.log(solve("ABCBDAB", "BDCABA"));
```

## Matrix-chain multiplication

We use `dp[i][j]` where `1<=i<=j<=n` to store the optimal cost when multiplying matrices $A_{i} A_{i+1} \dots A_{j-1} A_{j}$. And we hope we will get the final answer in `dp[1][n]`.

We use `p[i]` where `0<=i<=n` to store the size information of matrices. For example, the size of matrix $A_{1}$ is `p[0] * p[1]`, the size of matrix $A_{2}$ is `p[1] * p[2]`, ..., the size of matrix $A_{i}$ is `p[i - 1] * p[i]`. 

Since that, we know the cost to compute $A_{i} A_{i+1}$ (i.e. the number of times to multiply) is `p[i - 1] * p[i] * p[i + 1]`. Further, if we have already know the optimal cost of multiplying matrices sequence $A_{i}A_{i+1} \dots A_{k-1} A_{k}$ as `dp[i][k]` and $A_{k+1} \dots A_{j-1} A_{j}$ as `dp[k+1][j]`, we can know the optimal cost of multiplying $A_{i} \dots A_{j}$ as `dp[i][j]` is `dp[i][k] + dp[k + 1][j] + p[i - 1] * p[k] * p[j]`.

Recursion for `1 <= i < j <= n`:

1. When `i == j`, we have `dp[i][j] = 0` since there is no matrices were multiplied here.
2. When `i < j`, we have `dp[i][j] = min{ dp[i][k] + dp[k + 1][j] + p[i - 1] * p[k] * p[j] }` for `i <= k < j`.

```javascript
function rebuild(status, i, j) {
    if (i == j) return `A${i}`;
    let k = status[i][j];
    return `(` + rebuild(status, i, k) + rebuild(status, k + 1, j) + ')';
}

function solve(p) {
    let dp = [];
    let status = [];
    let n = p.length - 1;
    // initalize
    for (let i = 0; i <= n; ++i) {
        dp[i] = [];
        dp[i][i] = 0;
        status[i] = [];
    }
    // complete dp & status
    for (let l = 2; l <= n; ++l) {
        for (let i = 1; i <= n - l + 1; ++i) {
            let j =  l + i - 1;
            dp[i][j] = Infinity;
            for (let k = i; k < j; ++k) {
                let temp = dp[i][k] + dp[k + 1][j] + p[i - 1] * p[k] * p[j];
                if (temp < dp[i][j]) {
                    dp[i][j] = temp;
                    status[i][j] = k;
                }
            }
        }
    }
    // rebuild
    return rebuild(status, 1, n);
}
console.log(solve([30, 35, 15, 5, 10, 20, 25]));
```

# Greedy Algorithms

## An activity-selection problem

```javascript
function solve(n, starts, ends) {
    let activity = [];
    for (let i = 0; i < n; ++i) activity.push(i);
    activity.sort((i, j) => ends[i] - ends[j])
    
    let ans = [activity[0]];
    let last_activity_end_time = ends[activity[0]];
    for (let i = 1; i < n; ++i) {
        let cur = activity[i];
        if (starts[cur] >= last_activity_end_time) {
            ans.push(cur);
            last_activity_end_time = ends[cur];
        }
    }
    return ans;
}
console.log(solve(11, [1,3,0,5,3,5,6,8,8,2,12], [4,5,6,7,9,9,10,11,12,14,16]));
```