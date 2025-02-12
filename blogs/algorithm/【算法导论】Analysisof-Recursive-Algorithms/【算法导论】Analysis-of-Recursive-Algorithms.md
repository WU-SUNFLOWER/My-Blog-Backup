![113276050_p0 (1).jpg](image/cbf6e907e063786a7e5c1084ea5202b099e4234214cf11c82cbd02c067b1ecbc.image)

### 知识点回顾

#### Master Theorem

对于形如$T(n) = aT(n/b) + f(n)$（其中常数$a≥1, b>1$，$f(n)$是一个函数，表示递归函数分解与合并子问题的时间总开销）的递归式，有以下结论：

1. 若存在$ε>0$，使得$f(n) = O(n^{\log_b {a} - ε})$，即当$n→∞$时，$f(n)$在多项式意义上小于$\log_b {a}$，我们有$T(n) = Θ(n^{\log_b a})$ .
2. 若$f(n) = Θ(n^{\log_b a})$，我们有$T(n) = Θ(n^{\log_b a} \log {n})$ .
3. 若存在$ε>0$，使得$f(n) = Ω(n^{\log_b {a} + ε})$（即当$n→∞$时，$f(n)$在多项式意义上大于$\log_b {a}$），同时又存在某个常数$c < 1$，使得当$n→∞$时满足$af(n/b) ≤ cf(n)$，我们有$T(n) = Θ(f(n))$ .



### 习题

**对于下列递归式，给出T(n)的渐进上界和渐进下界。假定对于足够小的n，T(n)是常数。请给出尽量紧确的界，并验证其正确性。**

**（1）$T(n) = T(n-2) + n^2$**

**解：**

我们首先尝试通过换元构造形如$T(n) = aT(n/b) + f(n)$的递推式，再通过Master Theorem求解。

通过观察题目中的式子，我们发现$n - 2$这个结构比较讨厌。但同时我们又比较容易想到利用对数的性质来将其转化为乘积的形式。

令$n = \log_{2} m$，再利用对数的基本性质进行处理，

则原递归式化为$T(\log_{2} m) = T(\log_{2} \frac{m}{4}) + (\log_{2} m) ^ 2$

令$S(m) = T(\log_{2} m)$，

可进一步将原递归式化为$S(m) = S(\frac{m}{4}) + (\log_{2} m) ^ 2$

于是$a = 1, b = 4, f(m) = (\log_{2} m) ^ 2, m^{\log_{b} a} = 1$

显然，$f(m) = Ω(m^{\log_{b} a})$

但是，通过高数极限的知识，我们很容易证明，我们无法找到$ε > 0$，使得$f(m) = Ω(m^{\log_{b} {a+ε}})$

即不存在$ε > 0$，使得$f(m) = Ω(m^{ε})$，Master Theorem失效！

于是我们只能另觅他法。由于题目中的递归式在每次递归时，只会产生一个新的子问题，我们不妨直接对递归式进行展开。

我们知道，当$n → ∞$时，无论，并不会对递归函数的时间复杂度产生任何影响。所以这里为了方便起见，我们不妨直接令$n$为一个奇数。

$T(n) = T(n-2) + n^2$

$T(n) = T(n-4) + (n-2)^2 + n^2$

$T(n) = T(n-6) + (n-4)^2 + (n-2)^2 + n^2$

$\cdots$

$T(n) = T(1) + 3^2 + 5^2 + \cdots + (n-4)^2 + (n-2)^2 + n^2$

这里我们需要用到一个[结论](https://www.youtube.com/watch?v=vALS3Dvhv4Y)：$1^2 + 3^2 + 5^2 + \dots + (2t-1)^2 = \frac{t(4t^2-1)}{3}$

透过这个结论，再加之题干中告诉我们$T(1)$是个常数，我们可以很容易地判断出$T(n)$应为一个最高次项为$n^3$的多项式。

于是$T(n) = Θ(n^3)$，搞定！

**（2）$T(n) = 3T(\sqrt[3]{n}) + Θ(n)$**

**解：**

拿到递归式，先把渐进符号去掉，得$T(n)=3T(n^{\frac{1}{3}})+cn$，其中$c>0$.

换元，令$2^m = n$，则$m=\log_2 {n}$，原式化为$T(2^m)=3T(2^{\frac{m}{3}}) + c \cdot 2^m$

我们发现等式两侧出现了相似结构，接下来进行同构。令$S(m)=T(2^m)$

则原式化为$S(m)=3S(\frac{m}{3}) + c \cdot 2^m$

于是$a=3, b=3, f(m)=c \cdot 2^m, m^{\log_b a}=m$

显然，$f(m)=Ω(m^{\log_b a})$

更进一步地，若取$\varepsilon = 1$，可得$f(m)=Ω(m^{\log_{b}{a} + 1})=Ω(m^2)$，即$f(m)$在多项式意义上大于$m^{\log_b a}$.

再来检查"正则条件"，即是否存在$d < 1$，使得$af(\frac{m}{b}) \le df(m)$

经过对不等式的简单分析，注意到若取$d = \frac{1}{2}$，即可满足"正则条件"（事实上有无穷多个取法，验证"正则条件"举出一个例子即可）.

由Master Theorem，$S(m)=Ω(f(m))=Θ(2^m)$

于是$T(n)=T(2^m)=S(m)=Θ(2^m)$

**（3）$T(n) = T(\frac{n}{2}) + T(\frac{n}{4}) + T(\frac{n}{8}) + n$**

**解：**

这题中的递归式会把原问题分解成三个规模不同的子问题进行求解，因此无法采用Master Theorem或Recurrence Tree进行求解。

但是通过画前几层递归树找规律的方法，我们可以大胆猜出该递归式的上界至多为$O(n)$.

下面我们使用数学归纳法证明我们的猜测。

要证明存在$c>0$，使得$T(n) \le c \cdot n$

假设$T(\frac{n}{2}) \le c \cdot \frac{n}{2}$, $T(\frac{n}{4}) \le c \cdot \frac{n}{4}$, $T(\frac{n}{8}) \le c \cdot \frac{n}{8}$

那么只需取$c \ge 8$，可得$T(n) \le \frac{7}{8}cn+n \le cn$，即$T(n)=O(n)$

**（4）$T(n) = 2T(\sqrt{n}) + Θ(\log_2 {n})$**

**解：**

拿到递归式，先把渐进符号去掉，得$T(n) = 2T(\sqrt{n}) + c\log{n}$，其中常数$c > 0$

下面利用换元法对原式进行同构处理。

令$m = \log_2 {n}$，则$n = 2 ^ m$

于是原式转化为$T(2^m) = 2T(2^{\frac{m}{2}}) + cm$

我们发现等式两侧已经出现了相似结构，接下来可以构造适用Master Theorem的式子了。

令$S(m) = T(2^m)$，则原式转化为$S(m)=2S(\frac{m}{2}) + cm$

于是$a=2, b=2, f(m)=cm, m^{\log_{b} {a}}=m$，可见$f(m)=Θ(m^{\log_b {a}})$

由Master Theorem，可得$S(m)=Θ(m^{\log_b {a}}\log_2 m)=Θ(m\log_2 m)$

回代$S(m) = T(2^m)$，得到$T(2^m)=Θ(m\log_2 m)$

最后我们将$m = \log_2 {n}$回代，得到最终答案$Θ(\log_2 n \log_2( {\log_2 n}))$

**（5）$T(n) = \sqrt{n} T(\sqrt{n}) + n$**

这题的同构还是比较明显的，原式可化为$\frac{T(n)}{n}=\frac{T(\sqrt{n})}{\sqrt{n}}+1$

接下来我们用换元法消除式子中的$\sqrt{n}$，令$n=2^m, m=\log_2 {n}$

原式进一步化为$\frac{T(2^m)}{2^m}=\frac{T(2^\frac{m}{2})}{2^\frac{m}{2}}+1$

令$S(m)=\frac{T(2^m)}{2^m}$，则有$S(m)=S(\frac{m}{2})+1$

于是$a=1, b=2, m^{\log_b a}=1, f(m)=1$，可见$f(m)=Θ(m^{\log_b a})=Θ(1)$

由Master Theorem，$S(m)=Θ(\log_2 m)$

经过回代，可得到最终答案$T(n)=Θ(n\log_2 {(\log_2 {n})})$