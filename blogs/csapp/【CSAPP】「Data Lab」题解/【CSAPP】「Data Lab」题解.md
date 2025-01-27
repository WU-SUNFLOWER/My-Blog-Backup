
![108566149_p0.jpg](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b504769967b64ab789214d67cb14c78a~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1206&h=1711&s=461749&e=jpg&b=fcf7ea)

作为一名初学者，在做完CSAPP课程的「Data Lab」实验之后，我仍然感到回味无穷，惊叹于CMU教授们设计的Puzzles质量之高与解法之巧——即只利用最基本的位运算，来实现一些在编程中人们早已习以为常的运算。

这里先把题解代码挂上，详细的文字解析与推导日后有空再作补充。

### 第一部分：关于整形的问题

#### bitXor

```c++
int bitXor(int x, int y) {
  return ~(~(~x & y) & ~(x & ~y));
}
```

### tmin

```c++
int tmin(void) {
  return 1 << 31;
}
```

### isTmax

```c++
int isTmax(int x) {
    return !(~(x ^ (x + 1))) & !!(x + 1);
}
```

### allOddBits
```c++
int allOddBits(int x) {
  int symbol = 0x55;
  symbol |= symbol << 8;
  symbol |= symbol << 16;
  return !(~(x | symbol));
}
```

### negate
```c++
int negate(int x) {
  return ~x + 1;
}
```

### isAsciiDigit

```c++
int isAsciiDigit(int x) {
  // 0x30 = 0000 0000 0011 0000
  // 0x31 = 0000 0000 0011 0001
  // ...
  // 0x38 = 0000 0000 0011 1000
  // 0x39 = 0000 0000 0011 1001
  // larger 0000 0000 0011 1010
  //        0000 0000 0011 1011
  //        0000 0000 0011 1100
  //        0000 0000 0011 1101
  //        0000 0000 0011 1110
  //        0000 0000 0011 1111
  int ahead = !((x >> 4) ^ 0x03);
  int lower4Bits = x & 0xF;
  int carry = lower4Bits + 0b0110;
  return ahead & !(carry >> 4);
}
```

### conditional

```c++
int conditional(int x, int y, int z) {
  // x=false => !x=0000 0001 => ~(!x)=1111 1110 => ~(!x) + 1=1111 1111
  // => ~(~(!x) + 1)=0000 0000
  // x=true  => !x=0000 0000 => ~(!x)=1111 1111 => ~(!x) + 1=0000 0000
  // => ~(~(!x) + 1)=1111 1111
  unsigned int flag = ~(!x) + 1;
  return (~flag & y) | (flag & z);
}
```

### isLessOrEqual

```c++
int isLessOrEqual(int x, int y) {
  int isEqual = !(x ^ y);
  unsigned int ux = x;
  unsigned int uy = y;
  int symbolCheck1 = (ux >> 31) & !(uy >> 31); 
  int symbolCheck2 = !(ux >> 31) & (uy >> 31);
  unsigned int sub = x + (~y + 1);
  unsigned int flag = sub >> 31; // x<y, flag=1
  return (isEqual | flag | symbolCheck1) & !symbolCheck2;
}
```

### logicalNeg

```c++
int logicalNeg(int x) {
    unsigned int ux = x;
    unsigned int flag = (ux | (~ux + 1)) >> 31;
    return 1 ^ flag;
}
```

### howManyBits

其实我个人觉得这题在表述上是有一点点小问题的：题干中提示`howManyBits(-1) = 1`，但如果从补码的设计初衷出发的话，补码除了用低位储存信息外，必须预留出一位最高位用作标记该数是否是负数。因此从这个角度来看的话，`-1`的补码应当至少有2个bit。

不过，结合出题人给出的其他几个Examples来看的话，这题的本意应该还是让我们去计算从高位向低位数，第一个出现的`1`及其后面的比特位的总个数（这是非负数的情况，负数也可以transform成这种形式），再加上符号位一个bit得出最终结果。

```c++
int howManyBits(int x) {
    int bit16, bit8, bit4, bit2, bit1;
    // Here is an algorithmic right shift
    // For x >= 0, the mask is 0000...0000
    // For x < 0, the mask is 1111...1111
    int mask = x >> 31;
    // It's easy to prove that:
    // For x >= 0, the bit-level representation of x doesn't change
    // For x < 0, the representation is transformed as 0000...1...
    x = x ^ mask;

    bit16 = !!(x >> 16) << 4;
    x >>= bit16;
    bit8 = !!(x >> 8) << 3;
    x >>= bit8;
    bit4 = !!(x >> 4) << 2;
    x >>= bit4;
    bit2 = !!(x >> 2) << 1;
    x >>= bit2;
    bit1 = !!(x >> 1);
    x >>= bit1;

    return bit16 + bit8 + bit4 + bit2 + bit1 + x + 1;
}
```

### 第二部分：关于浮点型的问题

从该部分开始，题目允许我们使用任意的针对整型的运算，以及循环语句、条件语句等C语言语法，来模拟对单精度浮点数的一些运算。

在正式开始解题前，为了简化对单精度浮点数的操作，我事先定义了一套工具宏：

```c++
#define getSign(x) ((x) >> 31)
#define getExp(x) (((x) & 0x7f800000) >> 23)
#define getFrac(x) ((x) & 0x007fffff)

#define isNormalized(x) (getExp(x) != 0x00 && getExp(x) != 0xff)
#define isDeNormalized(x) (getExp(x) == 0x00)

#define isFinity(x) (getExp(x) == 0xff && getFrac(x) == 0x00)
#define isNaN(x) (getExp(x) == 0xff && getFrac(x) != 0x00)

#define packFloatNumber(sign, exp, frac) (((sign) << 31 ) | ((exp) << 23) | (frac))

#define Infinity 0x7f800000
#define NegInfinity 0xff800000
```

### floatScale2

```c++
unsigned floatScale2(unsigned uf) {
  unsigned int sign = getSign(uf);
  unsigned int exp = getExp(uf);
  unsigned int frac = getFrac(uf);
  if (isNormalized(uf)) {
    if (exp == 254) {
      return sign ? NegInfinity : Infinity;
    }
    return packFloatNumber(sign, exp + 1, frac);
  }
  else if (isFinity(uf) || isNaN(uf)) {
    return uf;
  }
  else {
    return packFloatNumber(sign, exp, frac << 1);
  }
}
```

### floatFloat2Int

这里题干虽然没有说明要使用哪种取整方式，但从实际测试来看，只需要实现与C语言中强制类型转换效果相同的「round towards zero」即可通过测试。

也就是说，对于原浮点数的小数部分，我们在处理时只需直接抛弃即可。

```c++
int floatFloat2Int(unsigned uf) {
    int sign = getSign(uf);
    int exp = getExp(uf);
    int E = exp - 127;
    unsigned int frac = getFrac(uf);
    // For f is in the range (-1, 1)
    if (E < 0) return 0;
    // For f is larger than the max value of integer
    // Infinity and NaN will be dealt with here as well.
    if (E >= 31) return 0x80000000;
    if (E <= 23) {
      // For floating-point numbers with small values,
      // the decimal places will be directly truncated.
      frac >>= 23 - E;
    } else {
      frac <<= E - 23;
    }
    unsigned int ans = (1 << E) | frac;
    ans *= sign ? -1 : 1;
    return ans;
}
```

### floatPower2

``` c++
unsigned floatPower2(int x) {
    if (x < -149) {
      return 0x00;
    }
    // If the answer is to be stored as a denormalized floating-point number
    else if (-149 <= x && x < -126) {
      return packFloatNumber(0, 0, 1 << (x + 149));
    }
    // If the answer is to be stored as a normalized floating-point number
    else if (-126 <= x && x <= 127) {
      return packFloatNumber(0, x + 127, 0);
    }
    else {
      return Infinity;
    }
}
```