![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/2e98f9c919b447dfb2d940831983bb6a~tplv-k3u1fbpfcp-jj-mark:660:660:0:0:q75.avis#?w=1334&h=1840&s=1033535&e=png&a=1&b=e0937b)


# Single-Source Shortest Paths

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c8199a5efa9447d1b52c6b0081f26530~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=499&h=357&s=32806&e=png&b=fffbfb)

## The Bellman-Ford algorithm

该算法用于计算**一般带权有向图**的单源最短路，**支持检测负权环**。

### 原理

### 复杂度

该算法进行$|V|-1$次迭代，每次迭代都需要对所有的边进行一次松弛操作。最后算法退出后，对所有的边再进行一次检查，以确认是否存在负权环（这部分可选）。

因此该算法的时间开销为$O(VE + E) = O(VE)$.

### 代码

```javascript
function bellman_ford(n, edges, start) {
    // initialize
    let graph = new Array(n).fill(0).map(_ => Array(n).fill(0))
    edges.forEach(edge => {
        let u = edge[0] = edge[0].charCodeAt(0) - 65;
        let v = edge[1] = edge[1].charCodeAt(0) - 65;
        graph[u][v] = edge[2];
    });
    start = start.charCodeAt(0) - 65;
    
    let dist = Array(n).fill(Infinity);
    let parent = Array(n).fill(-1);
    dist[start] = 0;  // the shorest path from start to start is zero.
    
    // relax all the edges n-1 times.
    for (let i = 0; i < n - 1; ++i) {
        for (let [u, v] of edges) {
            let weight = graph[u][v];
            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                parent[v] = u;
            }
        }
    }
    
    // check if negative-weight cycles exist.
    for (let [u, v] of edges) {
        if (dist[u] + graph[u][v] < dist[v]) {
            console.error("The graph contains negative-weight cycle(s).");
        }
    }
    
    // output
    for (let u = 0; u < n; ++u) {
        if (u === start) continue;
        let path = [u];
        let p = parent[u];
        while (p != -1) {
            path.unshift(p);
            p = parent[p];
        }
        console.log(path.map(u => String.fromCharCode(u + 65)).join('->'), `cost=${dist[u]}`);
    }
}

bellman_ford(5, [
    ['A', 'B', 10],
    ['A', 'D', 5],
    ['B', 'D', 2],
    ['D', 'B', 3],
    ['B', 'C', 1],
    ['D', 'C', 9],
    ['D', 'E', 2],
    ['C', 'E', 4],
    ['E', 'C', 6],
    ['E', 'A', 7]
], 'A');
```

## Dijkstra’s algorithm

适用范围：用于计算**不含负权边**的带权有向图的单源最短路径。

### 原理

单源最短路问题具有**贪心选择性质**和**最优子结构**，故可构建贪心算法求解

### 复杂度

由于Dijkstra算法执行过程中需要访问当次迭代的节点的所有邻接节点，出于性能考虑理想情况下我们应用该算法时应基于邻接链表来构建图。在此前提下，我们认为访问某个节点的所有邻接节点，其开销是$O(1)$的。

一般地，我们基于二叉堆来构建该算法的最小优先队列。
1. 初始化二叉堆的开销为$O(\log{V})$。
2. 每次从最小堆弹出`dist`值最小元素的开销为$O(\log {V})$，这个弹出操作要执行$|V|$次，因此总开销为$O(V \log {V})$。
3. 每次松弛操作对节点`dist`值进行更新操作后调整二叉堆的开销为$O(\log {V})$，而最坏情况下，图中的每条边都要进行一次松弛（当然这些松弛操作会分散在算法的若干次迭代之中），故这部分的总开销为$O(E \log {V})$.

综上所述，Dijkstra算法的时间复杂度为$O(\log{V}) + O(V \log {V}) + O(E \log {V}) = O((V + E) \log {V})$。一般的图都是比较稠密的，即$E >> V$，因此我们可以认为该算法的时间开销为$O(E \log {V})$，好于Bellman-Ford算法.

### 代码

这仅仅是一个演示代码，为了方便编码，我们基于邻接矩阵而非邻接链表来构建图，并且用简单的排序来代替算法中需要用到的优先队列。

```javascript
function dijkstra(n, edges, start) {
    let graph = new Array(n).fill(0).map(_ => Array(n).fill(0))
    edges.forEach(edge => {
        let u = edge[0].charCodeAt(0) - 65;
        let v = edge[1].charCodeAt(0) - 65;
        graph[u][v] = edge[2];
    });
    start = start.charCodeAt(0) - 65;
    
    let dist = Array(n).fill(Infinity);
    let parent = Array(n).fill(-1);
    let vertex = Array(n).fill(0).map((_, i) => i);
    dist[start] = 0;  // the shorest path from start to start is zero.
    while (vertex.length > 0) {
        vertex.sort((u, v) => dist[u] - dist[v]);
        let nearest = vertex.shift(); // select the vertex has the shortest distance with start currently.
        for (let next = 0; next < n; ++next) {
            let weight = graph[nearest][next];
            // relax all the vertices adjacent with nearest vertex.
            if (weight > 0 && dist[nearest] + weight < dist[next]) {
                dist[next] = dist[nearest] + weight;
                parent[next] = nearest;
            }
        }
    }
    
    for (let u = 0; u < n; ++u) {
        if (u === start) continue;
        let path = [u];
        let p = parent[u];
        while (p != -1) {
            path.unshift(p);
            p = parent[p];
        }
        console.log(path.map(u => String.fromCharCode(u + 65)).join('->'), `cost=${dist[u]}`);
    }
}

dijkstra(5, [
    ['A', 'B', 10],
    ['A', 'D', 5],
    ['B', 'D', 2],
    ['D', 'B', 3],
    ['B', 'C', 1],
    ['D', 'C', 9],
    ['D', 'E', 2],
    ['C', 'E', 4],
    ['E', 'C', 6],
    ['E', 'A', 7]
], 'A');
```

# All-Pairs Shortest Paths


![无标题.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c602b319ea6c4f5a9b1e4ba80b02684a~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=748&h=641&s=47750&e=png&b=fefbfb)

## The Floyd-Warshall algorithm

该算法用于计算一般的带权有向图（**允许含有负权边，但不能有负权环**）的所有节点对最短路径。

### 原理

该算法基于动态规划。根据教材中的设计思路，有如下的状态转移方程：

$d_{ij}^{(k)}$ denotes the element in $n × n$ matrix $D^{(k)}$.

If all the vertices are numbered as 0, 1, 2, ..., for $-1 ≤ k < n$:

1. When $k=-1$, we have $d_{ij}^{(k)} = w_{ij}$ as initial value.
2. When $k≥0$, we have $d_{ij}^{(k)} = \min \{ d_{ij}^{(k-1)}, d_{ik}^{(k-1)} + d_{kj}^{(k-1)} \}$.

很显然，如果按这个状态转移方程进行实现，我们就需要开辟n个n×n矩阵的空间，算法的空间复杂度将高达$Θ(n^3)$！下面我们证明我们只需要一个矩阵即可实现该算法。

假如我们只在一个矩阵中进行操作，则对于状态转移方程的第二行，即递推计算$d_{ij}^{(k)}$时，可能出现如下的几种情况：

1. $d_{ij}^{(k)} = \min \{ d_{ij}^{(k-1)}, d_{ik}^{(k-1)} + d_{kj}^{(k-1)} \}$

1. $d_{ij}^{(k)} = \min \{ d_{ij}^{(k-1)}, d_{ik}^{(k)} + d_{kj}^{(k-1)} \}$

1. $d_{ij}^{(k)} = \min \{ d_{ij}^{(k-1)}, d_{ik}^{(k-1)} + d_{kj}^{(k)} \}$

1. $d_{ij}^{(k)} = \min \{ d_{ij}^{(k-1)}, d_{ik}^{(k)} + d_{kj}^{(k)} \}$

第一种情况下，即为原始版本的Floyd-Warshall算法.

下面来看看后面的三种情况. $d_{ik}^{(k)}$表示的是一条从节点$i$到节点$k$的一条最短路径，且该路径的所有内部节点均取自集合$\{0, 1, \dots, k\}$，而由于$k$在端点上，不可能为最短路径的内部节点，所以该最短路径上的内部节点应出自集合$\{0,1,\dots,k-1\}$，即$d_{ik}^{(k)} = d_{ik}^{(k-1)}$，也就是说在算法连续两次的迭代过程中$d_{ik}$的取值并未发生变化. 同样地，我们知道$d_{kj}^{(k)} = d_{kj}^{(k-1)}$. 因此，在对单个矩阵原地操作版本的Floyd算法的某次迭代过程中计算$d_{ij}^{(k)}$时，我们总能保证原始版本Floyd算法的状态转移方程$d_{ij}^{(k)} = \min \{ d_{ij}^{(k-1)}, d_{ik}^{(k-1)} + d_{kj}^{(k-1)} \}$在改进版本的算法中仍然有效。

### 复杂度

空间复杂度$Θ(n^2)$，时间复杂度$Θ(n^3)$

### 代码

```JavaScript
function floyd(n, edges) {
    // initialze
    let dp = [];
    let parent = [];
    for (let i = 0; i < n; ++i) {
        // At first, we assume all the distances between different nodes is ∞.
        // It's obvious that the distance from a node to itself should be zero.
        dp[i] = Array(n).fill(Infinity);
        dp[i][i] = 0;
        // we record the predecessor for node v in the shortest path from u to v as parent[u][v].
        parent[i] = Array(n).fill(null);
    }
    for (let [u, v, distance] of edges) {
        u = u.charCodeAt() - 65;
        v = v.charCodeAt() - 65;
        dp[u][v] = distance;
        parent[u][v] = u;
    }
    // dynamic programming
    for (let k = 0; k < n; ++k) {
        for (let i = 0; i < n; ++i) {
            for (let j = 0; j < n; ++j) {
                if (dp[i][k] + dp[k][j] < dp[i][j]) {
                    dp[i][j] = dp[i][k] + dp[k][j];
                    parent[i][j] = parent[k][j];
                }
            }
        }
    }
    // ouput
    for (let i = 0; i < n; ++i) {
        for (let j = 0; j < n; ++j) {
            if (i === j) continue;
            
            let cur = j;
            let path = [];
            while (cur !== null) {
                path.unshift(cur);
                cur = parent[i][cur];
            }
            path = path.map(u => String.fromCharCode(u + 65)).join('->');
            
            console.log(`The shortest path from ${String.fromCharCode(i + 65)} ` + 
                        `to ${String.fromCharCode(j + 65)} costs ${dp[i][j]}.`);
            console.log(`The shortest path is ${path}`);
        }
    }
}

floyd(5, [
    ['A', 'B', 3],
    ['A', 'C', 8],
    ['A', 'E', -4],
    ['B', 'E', 7],
    ['B', 'D', 1],
    ['C', 'B', 4],
    ['D', 'C', -5],
    ['D', 'A', 2],
    ['E', 'D', 6]
]);
```

# Minimum Spanning Trees

下面的两种计算MST的算法在本质上都是贪心算法。

## Prim

### 复杂度

Prim算法的复杂度分析与Dijkstra算法类似。对于基于邻接链表构建的图，和基于二叉堆构建的优先队列：

1. 初始化`dist`和`parent`数组花费$O(V)$.
2. 每次从二叉堆中弹出顶点花费$O(\log {V})$，共要弹出$|V|$次，总开销$O(V \log {V})$.
3. 每次更新`dist`数组都要顺带调整最小堆，最坏情况下访问图中的每条边后都要进行更新，总开销为$O(E \log {V})$.

与Dijkstra算法类似，一般地Prim的时间复杂度为$O(E \log {V})$

### 代码

```javascript
function solve(n, edges) {
    // initialize the graph
    let graph = Array(n).fill(0).map(_ => Array(n).fill(0));
    let base = 'a'.charCodeAt(0);
    for (let edge of edges) {
        let u = edge[0].charCodeAt(0) - base;
        let v = edge[1].charCodeAt(0) - base;
        graph[u][v] = graph[v][u] = edge[2];
    }
    // initialize
    let parent = Array(n);
    let dist = Array(n).fill(Infinity);
    let vertices = [];  // to store the vertices haven't be "dragged" to MST yet.
    for (let i = 0; i < n; ++i) vertices.push(i);
    dist[0] = 0;
    
    // generate the MST
    while (vertices.length > 0) {
        let nearest_vertex;
        // since this is a simple version of Prim, 
        // we just use sorting instead of a min heap.
        vertices.sort((u, v) => dist[u] - dist[v]);  
        nearest_vertex = vertices.shift();
        for (let adj_vertex = 0; adj_vertex < n; ++adj_vertex) {
            let new_dist = graph[nearest_vertex][adj_vertex];
            if (new_dist != 0 && new_dist < dist[adj_vertex] && vertices.includes(adj_vertex)) {
                dist[adj_vertex] = new_dist;
                parent[adj_vertex] = nearest_vertex;
            }
        }
    }
    
    // output
    let sum_cost = 0;
    for (let u = 1; u < n; ++u) {
        console.log(`${String.fromCharCode(parent[u] + base)} ${String.fromCharCode(u + base)}`);
        sum_cost += dist[u];
    }
    console.log(`The sum cost of MST is ${sum_cost}.`);
}

let edges = [
    ['b', 'c', 8],
    ['c', 'd', 7],
    ['a', 'b', 4],
    ['i', 'c', 2],
    ['e', 'd', 9],
    ['h', 'a', 8],
    ['h', 'b', 11],
    ['h', 'i', 7],
    ['h', 'g', 1],
    ['g', 'i', 6],
    ['g', 'f', 2],
    ['f', 'c', 4],
    ['f', 'd', 14],
    ['f', 'e', 10],
];
solve(9, edges);
```

## Kruskal

### 复杂度

$O(E \log {V})$

### 代码

```javascript
function InitSet(n) {
    let set = [];
    for (let i = 0; i < n; ++i) set.push(i);
    return set;
}

function FindSet(set, i) {
    if (set[i] === i) {
        return i;
    } else {
        return (set[i] = FindSet(set, set[i]));
    }
}

function UnionSet(set, i, j) {
    set[i] = set[j];
}

function solve(n, edges) {
    // pre-process edges
    let base = 'a'.charCodeAt(0);
    for (let edge of edges) {
        edge[0] = edge[0].charCodeAt(0) - base;
        edge[1] = edge[1].charCodeAt(0) - base;
    }

    /* generate the MST */
    // here we use a disjoint set to record the connect-components which our edges belong to.
    let set = InitSet(n);  
    let edges_mst = [];
    edges.sort((e1, e2) => e1[2] - e2[2]);
    while (edges.length > 0) {
        let cur_edge = edges.shift();
        let [u, v, weight] = cur_edge;
        if (FindSet(set, u) !== FindSet(set, v)) {
            edges_mst.push(cur_edge);
            // now the vertex u and v are in the same connect-components,
            // so we need to union their original connect-components.
            UnionSet(set, u, v);
        }
    }
    
    // output
    let sum_cost = 0;
    for (let [u, v, weight] of edges_mst) {
        console.log(`${String.fromCharCode(u + base)} ${String.fromCharCode(v + base)}`);
        sum_cost += weight;
    }
    console.log(`The sum cost of MST is ${sum_cost}.`);
}

let edges = [
    ['b', 'c', 8],
    ['c', 'd', 7],
    ['a', 'b', 4],
    ['i', 'c', 2],
    ['e', 'd', 9],
    ['h', 'a', 8],
    ['h', 'b', 11],
    ['h', 'i', 7],
    ['h', 'g', 1],
    ['g', 'i', 6],
    ['g', 'f', 2],
    ['f', 'c', 4],
    ['f', 'd', 14],
    ['f', 'e', 10],
];
solve(9, edges);
```

