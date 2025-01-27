
![104128329_p0.jpg](https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/76e70f0b1edd4ed2844a87fab2410305~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=675&h=1000&s=722932&e=jpg&b=fbf4f2)

其实这是我自己准备期末考试时做的重要知识点梳理，题目都不是很难（因为这学期也没学啥很高阶的语法和技巧...），注重考察基础，主要是为了防止考试时出现低级错误，故特此整理。

### 1. 请阅读如下的C++代码并回答问题

```cpp
#include <iostream>
#include <string>

class Base {
public:
    virtual void func(int x) {
        std::cout << "Base::func(int): " << x << std::endl;
    }
    virtual void func(float x) {
        std::cout << "Base::func(float): " << x << std::endl;
    }
};

class Derived : public Base {
public:
    void func(int x) override {
        std::cout << "Derived::func(int): " << x << std::endl;
    }
    void func(double x) {
        std::cout << "Derived::func(double): " << x << std::endl;
    }
    void func(const std::string& x) {
        std::cout << "Derived::func(const std::string&): " << x << std::endl;
    }
    void func(const std::string&& x) {
        std::cout << "Derived::func(const std::string&&): " << x << std::endl;
    }
};

template<typename T>
void callFunc(Base* obj, T&& x) {
    dynamic_cast<Derived*>(obj)->func(std::forward<T>(x));
}

int main() {
    Derived d;
    Base* bPtr = &d;
    callFunc(bPtr, 2.33f);
    callFunc(bPtr, 10);
    callFunc(bPtr, 10.5);
    callFunc(bPtr, "Hello");
}
```

1. 请写出上述代码的输出结果。

2. 请对callFunc函数进行改造，使其能够根据传入指针所指向对象的实际类型，正确调用Base或Derived类的对应版本的func方法。

**参考答案**

1. 输出结果如下：

> Derived::func(double): 2.33
> 
> Derived::func(int): 10
> 
> Derived::func(double): 10.5
> 
> Derived::func(const std::string&&): Hello

2. 可对函数进行如下改造

```c++
template<typename T>
void callFunc(Base* obj, T&& x) {
    auto ptr = dynamic_cast<Derived*>(obj);
    if (ptr != nullptr) {
        ptr->func(std::forward<T>(x));
    } else {
        obj->func(std::forward<T>(x));
    }
}
```

注：修改完`callFunc`函数后，还需要为基类`Base`补充接收`main`主函数中出现的各种可能被传入的数据类型参数的`func`重载方法。

### 2. 请阅读如下的C++代码并回答问题

```cpp
#include <iostream>

class Component1 {
public:
    Component1(int v) {
        std::cout << "Component1 constructor. some value=" << v << std::endl;
    }
    ~Component1() {
        std::cout << "Component1 destructor\n";
    }
};

class Component2 {
public:
    Component2(int v) {
        std::cout << "Component2 constructor. some value=" << v << std::endl;
    }
    ~Component2() {
        std::cout << "Component2 destructor\n";
    }
};

class Base1 {
public:
    Base1(int v) {
        std::cout << "Base1 constructor. some value=" << v << std::endl;
    }
    virtual ~Base1() {
        std::cout << "Base1 destructor\n";
    }
};

class Base2 {
public:
    Base2(int v) {
        std::cout << "Base2 constructor. some value=" << v << std::endl;
    }
    virtual ~Base2() {
        std::cout << "Base2 destructor\n";
    }
};

class Derived : public Base1, public Base2 {
private:
    Component1 c1;
    Component2 c2;
public:
    Derived(int v1, int v2, int v3, int v4) : c2(v1), Base1(v2), c1(v3), Base2(v4) {
        std::cout << "Derived constructor\n";
    }
    ~Derived() {
        std::cout << "Derived destructor\n";
    }
};

int main() {
    Derived d(1, 2, 3, 4);
    return 0;
}
```

1. 请写出上述代码的输出结果。
2.  如果`Component`类也有一个显示的复制构造函数和赋值操作符重载，请说明它们何时会被调用。
3.  如果`Base`类声明了一个虚拟的复制构造函数，这会如何影响`Derived`类对象的构造过程？


**参考答案**

1. 输出结果如下：

> Base1 constructor. some value=2
> 
> Base2 constructor. some value=4
> 
> Component1 constructor. some value=3
> 
> Component2 constructor. some value=1
> 
> Derived constructor
> 
> Derived destructor
> 
> Component2 destructor
> 
> Component1 destructor
> 
> Base2 destructor
> 
> Base1 destructor

2. 这些特殊成员函数在本例中不会被调用，因为`Component`对象是作为`Derived`类的直接成员创建的。复制构造函数和赋值操作符通常在对象复制或赋值时调用。

3. 在C++中，虚拟复制构造函数是非法的。构造函数，包括复制构造函数，不能是虚拟的。因此，这个修改会导致编译错误。

### 3.写出以下C++代码的输出结果

```c++
#include <iostream>

using namespace std;

void fun(int test) {
    if (test == 0) throw test;
    if (test==1) throw 1.5;
    if (test==2) throw "abc";
    cout<<"fun调用正常结束"<<endl;
}

void caller1(int test) {
    try {
        fun(test);
    }
    catch (int) {
        cout << "caller1捕获int->";
    }
    cout << "caller1调用正常结束" << endl;
}

void caller2(int test) {
    try {
        caller1(test);
    } catch (double) {
        cout << "caller2捕获double->";
    } catch (...) {
        cout << "caller2捕获所有未知异常->";
    }
    cout << "caller2调用正常结束" << endl;
}

int main() { 
    for (int i = 3; i >= 0; i--) caller2(i); 
    return 0;
}
```

参考答案：

> fun调用正常结束
> 
> caller1调用正常结束
> 
> caller2调用正常结束
> 
> caller2捕获所有未知异常->caller2调用正常结束
> 
> caller2捕获double->caller2调用正常结束
> 
> caller1捕获int->caller1调用正常结束
> 
> caller2调用正常结束

### 4. 请阅读如下的C++代码并回答问题

```cpp
#include <iostream>

class Grandparent {
public:
    Grandparent() {
        std::cout << "Grandparent constructor\n";
    }
    void doSomething() {
        std::cout << "Grandparent action\n";
    }
    ~Grandparent() {
        std::cout << "Grandparent destructor\n";
    }
};

class Parent1 : public virtual Grandparent {
public:
    Parent1() {
        std::cout << "Parent1 constructor\n";
    }
    ~Parent1() {
        std::cout << "Parent1 destructor\n";
    }
};

class Parent2 : public virtual Grandparent {
public:
    Parent2() {
        std::cout << "Parent2 constructor\n";
    }
    ~Parent2() {
        std::cout << "Parent2 destructor\n";
    }
};

class Child : public Parent2, public Parent1 {
public:
    Child() {
        std::cout << "Child constructor\n";
    }
    ~Child() {
        std::cout << "Child destructor\n";
    }
};

int main() {
    Child c;
    c.doSomething();
    return 0;
}
```

1. 写出上述代码的输出结果
2. 解释虚继承在此代码中的作用，并说明为什么它是必要的

**参考答案**

1. 代码输出结果如下：

> Grandparent constructor
> 
> Parent2 constructor
> 
> Parent1 constructor
> 
> Child constructor
> 
> Grandparent action
> 
> Child destructor
> 
> Parent1 destructor
> 
> Parent2 destructor
> 
> Grandparent destructor

2. 虚继承确保在菱形继承结构中，最底部的派生类（Child）只有一个共享的基类实例（Grandparent）。这是必要的，因为非虚继承会导致Grandparent类的多个实例存在于Child中，这可能导致资源浪费和不一致的状态。

### 5. 程序设计题

设计一个简单的统计分析器，用于计算一系列数值的统计信息，如平均值、最大值和最小值。并在`main`函数中编写代码进行测试。

#### 要求

1.  **模板类**：创建一个模板类`Statistics`，用于处理不同数据类型（如`int`、`double`等）的统计计算。
1.  **仿函数**：通过重载`operator()`使得`Statistics`类的实例可以像函数一样被调用，用于向统计分析器中添加新的数据点。
1.  **静态成员**：在`Statistics`类中使用静态成员变量来存储所有实例共享的数据（如数据点的总数）。
1.  **静态成员函数**：提供一个静态成员函数来返回所有实例共享的数据。
1.  **重载运算符**：重载`<<`运算符以便于打印出统计分析结果（平均值、最大值和最小值）。

**参考答案**

```c++
#include <iostream>

template<typename T>
class Statistics {
private:
    int count;  // 记录当前对象采集的数据点总数
    T sum;  // 记录当前对象采集的数据点之和
    T minValue;  // 记录当前对象采集的数据点之中的最小值
    T maxValue;  // 记录当前对象采集的数据点之中的最大值
    bool flag;  // 记录当前对象是否完成初始化（即采集了第一个数据点）
    static int totalCount;  // 记录所有Statistics<T>对象采集的数据点总数
public:
    Statistics() : count(0), sum(0), flag(false), minValue(0), maxValue(0) {}
    Statistics& operator ()(T value) {
        ++count;
        ++totalCount;
        sum += value;
        if (flag) {
            minValue = std::min(minValue, value);
            maxValue = std::max(maxValue, value);
        } else {
            minValue = maxValue = value;
            flag = true;
        }
        return *this;
    }
    static int getTotalCount() {
        return totalCount;
    }
    template<typename U>
    friend std::ostream& operator<<(std::ostream& out, Statistics<U>& object);
};

template<typename T>
int Statistics<T>::totalCount = 0;

template<typename T>
std::ostream& operator<<(std::ostream& out, Statistics<T>& object) {
    out << "average=" << (object.sum / object.count) << ", minValue=" << object.minValue << ", maxValue=" << object.maxValue;
    return out;
}

int main() {
    Statistics<double> s1;
    Statistics<int> s2;
    s1(1.0);
    s1(2.0);
    s1(3.0);
    s2(7);
    s2(9);
    std::cout << s1 << std::endl;
    std::cout << s2 << std::endl;
    std::cout << Statistics<double>::getTotalCount() << std::endl;
    std::cout << Statistics<int>::getTotalCount() << std::endl;
}
```

### 6. 程序设计题

设计一个类似于std::string的类`MyString`，并编写main函数中的代码进行测试。这个类包含以下特点：
1. 支持不含任何参数的默认构造函数
2. 支持传入const char*指针创建对象
3. 支持移动语义
4. 重载运算符：+、+=、==、=、!=、\[]
5. 重载输入输出流：>>、<<

**参考答案**
```c++
#define _CRT_SECURE_NO_WARNINGS 1
#include <iostream>
#include <cstring>
#include <sstream>

class MyString {
private:
    char* buffer = nullptr;
    size_t capacity = 0;
public:
    MyString() {
        capacity = 4;
        buffer = new char[capacity];
        buffer[0] = '\0';
    }
    MyString(const char* src) {
        capacity = strlen(src) + 1;
        buffer = new char[capacity];
        strcpy(buffer, src);
    }
    MyString(const MyString& other) {
        capacity = other.length() + 1;
        buffer = new char[capacity];
        strcpy(buffer, other.buffer);
    }
    MyString(MyString&& other) noexcept {
        capacity = other.capacity;
        buffer = other.buffer;
        other.capacity = 4;
        other.buffer = new char[4];
        other.buffer[0] = '\0';
    }
    ~MyString() {
        delete[] buffer;
    }
    size_t length() const {
        return strlen(buffer);
    }
    char operator [](size_t idx) const {
        if (idx >= length()) throw std::out_of_range("index out of range");
        return buffer[idx];
    }
    char& operator [](size_t idx) {
        if (idx >= length()) throw std::out_of_range("index out of range");
        return buffer[idx];
    }
    MyString& operator =(const MyString& other) {
        size_t len_other = other.length();
        if (capacity <= len_other) {
            capacity = len_other + 1;
            delete[] buffer;
            buffer = new char[capacity];
        }
        strcpy(buffer, other.buffer);
        return *this;
    }
    MyString& operator += (const char ch) {
        size_t len = length();
        if (len + 1 >= capacity) {
            char* oldBuffer = buffer;
            capacity *= 1.5;
            buffer = new char[capacity];
            strcpy(buffer, oldBuffer);
            delete[] oldBuffer;
        }
        buffer[len] = ch;
        buffer[len + 1] = '\0';
        return *this;
    }
    MyString& operator += (const MyString& other) {
        size_t len_self = length();
        size_t len_other = other.length();
        if (len_self + len_other >= capacity) {
            char* oldBuffer = buffer;
            capacity = std::max(static_cast<size_t>(capacity * 1.5), len_self + len_other + 1);
            buffer = new char[capacity];
            strcpy(buffer, oldBuffer);
            delete[] oldBuffer;
        }
        strcpy(buffer + len_self, other.buffer);
        buffer[len_self + len_other] = '\0';
        return *this;
    }
    friend MyString operator +(const MyString& a, const MyString& b) {
        MyString object;
        size_t len_a = a.length();
        size_t len_b = b.length();
        size_t capacity = len_a + len_b + 1;
        delete[] object.buffer;
        object.buffer = new char[capacity];
        object.capacity = capacity;
        strcpy(object.buffer, a.buffer);
        strcpy(object.buffer + len_a, b.buffer);
        return object;
    }
    friend bool operator ==(const MyString& a, const MyString& b) {
        return strcmp(a.buffer, b.buffer) == 0;
    }
    friend bool operator !=(const MyString& a, const MyString& b) {
        return strcmp(a.buffer, b.buffer) != 0;
    }
    friend bool operator <(const MyString & a, const MyString & b) {
        return strcmp(a.buffer, b.buffer) < 0;
    }
    friend bool operator >(const MyString& a, const MyString& b) {
        return strcmp(a.buffer, b.buffer) > 0;
    }
    friend std::ostream& operator <<(std::ostream& out, const MyString& object) {
        out << object.buffer;
        return out;
    }
    friend std::istream& operator >>(std::istream& in, MyString& object) {
        char ch;
        bool flag = false;
        while (in.get(ch)) {
            if (ch != '\t' && ch != '\n' && ch != ' ') {
                flag = true;
                object += ch;
            } else if (flag) {
                break;
            }
        }
        return in;
    }
};

int main() {
    MyString str1 = "ABCDEFGHIJKL*";
    MyString str2 = "*DASJHILASDHJKLASDJKHADS";
    MyString str3, str4;
    std::cin >> str3;
    str4 = str1 + str2 + str3;
    std::cout << str4 << std::endl;

    str1 += str2;
    str1 += "2024";
    std::cout << str1 << std::endl;
    
    std::cout << "-----------------" << std::endl;

    std::cout << str1[0] << std::endl;
    str1[0] = 'X';
    std::cout << str1[0] << std::endl;
    return 0;
}
```

### 7. 填空题

以下运算符中，在C++中无法被重载的有____。

A.成员访问运算符（.）、B.成员指针访问运算符（->）、C.域作用符（::）、D.条件运算符（? :）、E.取地址运算符（&）、F.取值运算符（\*）、G. sizeof运算符、H. 等于比较运算符（==）

**参考答案** ACDG

**易错点说明**

与点运算符不同（.），你**可以重载**箭头运算符（->）。这通常用在实现智能指针或类似指针行为的类中。

以下是一个简单的例子：

```c++
#include <iostream>

using namespace std;

class MyClass {
public:
    MyClass* operator->() {
        return this;
    }
    void someFunction() {
        cout << "Hello World";
    }
};

int main() {
    MyClass obj;
    obj->someFunction(); // 通过重载的箭头运算符访问
}
```

### 8. 阅读如下的程序并回答问题

```c++
#include <iostream>

class Base {
public:
    void publicBaseMethod() {
        std::cout << "Base::publicBaseMethod" << std::endl;
    }
protected:
    void protectedBaseMethod() {
        std::cout << "Base::protectedBaseMethod" << std::endl;
    }
private:
    void* privatedBaseVar;
    void privateBaseMethod() {
        std::cout << "Base::privateBaseMethod" << std::endl;
    }
};

class Derived : protected Base {
public:
    void accessBaseMembers() {
        publicBaseMethod();  // Line1
        protectedBaseMethod();  // Line2
        this->Base::privateBaseMethod();  // Line3
    }
protected:
    void protectedDerivedMethod() {
        std::cout << "Derived::protectedDerivedMethod" << std::endl;
    }
};

class MultilevelDerived : private Derived {
public:
    void accessMembers() {
        publicBaseMethod();  // Line4
        protectedBaseMethod();  // Line5
        accessBaseMembers();  // Line6
        protectedDerivedMethod();  // Line7
    }
};

int main() {
    Derived d;
    MultilevelDerived mld;
    d.publicBaseMethod();  // Line8
    mld.accessMembers();  // Line9
    mld.accessBaseMembers();  // Line10
    return 0;
}
```

1. 请指出以上程序中，代码`Line1`~`Line10`中，哪几行的代码是**不符合**C++语法规范的？
2. 假设程序在x64平台编译，若在`main`函数中打印`sizeof(mld)`，则输出结果应为多少？

**参考答案**
1. 错误的代码如下：
```c++
class Derived : protected Base {
public:
    void accessBaseMembers() {
        publicBaseMethod();  // Line1
        protectedBaseMethod();  // Line2
        // this->Base::privateBaseMethod();  Line3错误！
    }
protected:
    void protectedDerivedMethod() {
        std::cout << "Derived::protectedDerivedMethod" << std::endl;
    }
};

class MultilevelDerived : private Derived {
public:
    void accessMembers() {
        publicBaseMethod();  // Line4
        protectedBaseMethod();  // Line5
        accessBaseMembers();  // Line6
        protectedDerivedMethod();  // Line7
    }
};

int main() {
    Derived d;
    MultilevelDerived mld;
    // d.publicBaseMethod();  Line8 错误！
    mld.accessMembers();  // Line9
    // mld.accessBaseMembers();  Line10 错误！
    return 0;
}
```
2. 打印结果为`8`

### 8. 选择题

以下**哪几组**函数声明及其定义是符合C++语法规则的？ 

选项A. 

```c++
int add(int a = 1, int b); 
int add(int a, int b = 2) { return a + b; }
``` 

选项B. 
```c++
int add(int a, int b = 2); 
int add(int a, int b = 2) { return a + b; }
``` 

选项C. 

```c++
int add(int a, int b); 
int add(int a, int b = 2) { return a + b; }
```

选项D. 

```c++
int add(int a, int b = 2) throw(...); 
int add(int a, int b) noexcept(true) { return a + b; }
```

选项E.
```c++
template<typename T, T D = 2>
T add(T a, T b = D) {
    return a + b;
}
```

**参考答案**   C、E

### 9. 请阅读以下的程序并回答问题

```c++
#include <iostream>
#include <vector>

class Example {
private:
    std::vector<int> vec(1, 2, 3);
    const int id;
    static int counter = 0;
    int something1 = 233;
    const int something2 = 8888;
    const static int something3 = 0;
public:
    Example() {
        this->id = GenerateId();
    }
    static int GenerateId() {
        return ++counter;
    }
    void print();
};

void Example::print() {
    std::cout << "id=" << id << ", vec=[";
    for (auto& v : vec) {
        std::cout << v << " ";
    }
    std::cout << "]" << std::endl;
}

int main() {
    const Example ex1;
    Example ex2;
    ex1.print();
    ex2.print();
    return 0;
}
```

在类Example，存在若干处不符合C++语法规范的错误，请指出并更正。

**参考答案**

```cpp
class Example {
private:
    // 对非静态成员变量进行类内初始化(in-class initialization)时
    // 需要使用initializer_list来实现
    std::vector<int> vec = {1, 2, 3};
    const int id;
    static int counter;
    int something1 = 233;
    const int something2 = 8888;
    const static int something3 = 0;
public:
    // 被const修饰的成员变量只能在成员初始化列表初始化
    Example() : id(GenerateId()) {}
    static int GenerateId() {
        static int counter = 0;
        return ++counter;
    }
    // 被const修饰的实例化对象无法调用未被const修饰的成员函数
    // 因此这里需要补一个const
    void print() const;
};

// 未被const修饰的静态成员变量只能在类外初始化
int Example::counter = 0;

// 类外定义应与类内声明的函数签名保持一致，这里也要加上const
void Example::print() const {
    std::cout << "id=" << id << ", vec=[";
    for (auto& v : vec) {
        std::cout << v << " ";
    }
    std::cout << "]" << std::endl;
}
```

### 10. 阅读如下程序并回答问题

```c++
#include <iostream>

class MyClass1 {
public:
    unsigned int x, y;
    MyClass1() = default;
};

class MyClass2 {
public:
    unsigned int x, y;
};

class MyClass3 {
public:
    unsigned int x, y;
    MyClass3() : x(20),y(24) {}
};

int main() {
    MyClass1* o1 = new MyClass1();
    MyClass1* o2 = new MyClass1;
    std::cout << o1->x << ", " << o1->y << std::endl;
    std::cout << o2->x << ", " << o2->y << std::endl;

    MyClass2* o3 = new MyClass2();
    MyClass2* o4 = new MyClass2;
    std::cout << o3->x << ", " << o3->y << std::endl;
    std::cout << o4->x << ", " << o4->y << std::endl;

    MyClass3* o5 = new MyClass3();
    MyClass3* o6 = new MyClass3;
    std::cout << o5->x << ", " << o5->y << std::endl;
    std::cout << o6->x << ", " << o6->y << std::endl;
}
```

1. 假设编译器默认为新分配的堆区内存空间填充字节`0xcd`，且在该编译环境下`unsigned int`型的变量占用4个字节，请写出上述代码的打印结果？

2. 如下的代码片段能否通过编译，为什么？

```cpp
#include <iostream>

class MyClass4 {
public:
    unsigned int x, y;
    MyClass4(unsigned int x, unsigned int y) : x(x), y(y) {}
};

int main() {
    MyClass4* o7 = new MyClass4;
    std::cout << o7->x << ", " << o7->y << std::endl; 
}
```

**参考答案**

1.输出结果：

> 0, 0
> 
> 3452816845, 3452816845
> 
> 0, 0
> 
> 3452816845, 3452816845
> 
> 20, 24
> 
> 20, 24

2. 不能通过编译。因为想要通过`new MyClass4`创建对象，则要求该类中必须含有一个形参列表为空的构造函数。而在`MyClass4`中，由于存在一个含有形参的构造函数，编译器不会创建不带任何形参的默认构造函数。因此在本题中编译器找不到合适的构造函数来配合执行`new MyClass4`，故无法通过编译。

### 11. 程序设计题

假设在当前目录下有一个名为`text.txt`的文本文件，请设计一个简单的文本处理程序，用于统计输入文本中每个单词的出现频率，并按频率从高到低排序输出每个单词及其对应的频率。要求使用`std::fstream`、`std::list`、和`std::map`来实现以下功能：

1. 使用`std::fstream`读取文件内容。
1. 使用`std::map`来存储每个单词及其出现的次数。
1. 使用`std::list`来实现单词的按频率排序功能，并将排序结果打印到屏幕上。

代码框架已给出，请在此基础上完成程序的设计：

```c++
#include <iostream>
#include <list>
#include <map>
#include <string>
#include <algorithm>
#include <fstream>

// 定义单词及其频率的结构
struct WordFreq {
    std::string word;
    int frequency;
};

void processInput(std::map<std::string, int>& wordMap) {
    // 实现细节: 读取文本，统计单词频率
}

void sortWords(const std::map<std::string, int>& wordMap, std::list<WordFreq>& sortedList) {
    // 实现细节: 将map中的数据转移到list，并按频率排序
}

void printAns(const std::list<WordFreq>& sortedList) {
    // 实现细节: 将排序后的数据打印输出
}

int main() {
    std::map<std::string, int> wordMap;
    std::list<WordFreq> sortedList;

    processInput(wordMap);         // 处理输入并统计频率
    sortWords(wordMap, sortedList); // 对单词进行排序
    printAns(sortedList);   // 输出结果

    return 0;
}
```

**参考答案**

```c++
#include <iostream>
#include <list>
#include <map>
#include <string>
#include <algorithm>
#include <fstream>

// 定义单词及其频率的结构
struct WordFreq {
    std::string word;
    int frequency;
};

void processInput(std::map<std::string, int>& wordMap) {
    char ch;
    std::string word = "";
    std::fstream file("text.txt", std::ios::in);
    while (file.get(ch)) {
        if ('A' <= ch && ch <= 'Z') {
            ch = 'a' + ch - 'A';
            word += ch;
        }
        else if ('a' <= ch && ch <= 'z') {
            word += ch;
        }
        else if (word.length() > 0) {
            wordMap[word] = wordMap.count(word) ? (wordMap[word] + 1) : 1;
            word = "";
        }
    }
    if (word.length() > 0) {
        wordMap[word] = wordMap.count(word) ? (wordMap[word] + 1) : 1;
    }
}

void sortWords(const std::map<std::string, int>& wordMap, std::list<WordFreq>& sortedList) {
    WordFreq temp;
    for (auto& elem: wordMap) {
        temp = {elem.first, elem.second};
        sortedList.push_back(temp);
    }
    sortedList.sort([](const WordFreq& a, const WordFreq& b) {
        return a.frequency < b.frequency;
    });
}

void printAns(const std::list<WordFreq>& sortedList) {
    for (auto iter = sortedList.begin(); iter != sortedList.end(); ++iter) {
        const WordFreq& elem = *iter;
        std::cout << elem.frequency << ". " << elem.word << std::endl;
    }
}

int main() {
    std::map<std::string, int> wordMap;
    std::list<WordFreq> sortedList;

    processInput(wordMap);         // 处理输入并统计频率
    sortWords(wordMap, sortedList); // 对单词进行排序
    printAns(sortedList);   // 输出结果

    return 0;
}
```

### 12. 程序设计题

设计一个类 CircularCounter，用于表达一个循环计数器的概念。
该计数器在达到一个固定的上限值后会循环回到初始值。请实现以下特性：

1. 构造函数接受3个参数：startValue、endValue、cur，前两者分别代表计数器的最大值和初始值，后者可设定初始计数值。计数器的值应该在 startValue 到 endValue 之间循环。
1. 实现前缀和后缀版本的 ++ 运算符重载。前缀版本应该增加计数器的值并返回当前对象的引用。后缀版本应该增加计数器的值，但返回计数器增加前的值的一个副本。
1. 重载输出运算符 <<，当计数器对象被传递给标准输出流时，应该输出计数器的当前值。

**参考答案**

```c++
#include <iostream>

class CircularCounter {
private:
    int cur;
    int startValue, endValue;
public:
    CircularCounter(int start, int end, int cur) : 
        startValue(start), endValue(end), cur(cur) {}
    CircularCounter(const CircularCounter& other) :
        startValue(other.startValue), endValue(other.endValue), cur(other.cur) {}
    // ++i
    CircularCounter& operator ++() {
        cur = ((cur - startValue) + 1) % (endValue - startValue + 1) + startValue;
        return *this;
    }
    // i++
    CircularCounter operator ++(int) {
        CircularCounter backup = *this;
        cur = ((cur - startValue) + 1) % (endValue - startValue + 1) + startValue;
        return backup;
    }
    // object前面的const修饰符不能漏，这样才能让重载函数接收后置++返回的右值
    friend std::ostream& operator <<(std::ostream& out, const CircularCounter& object) {
        out << object.cur;
        return out;
    }
};

int main() {
    CircularCounter c(1, 7, 1);
    std::cout << (++c) << std::endl;
    std::cout << (c++) << std::endl;
    std::cout << c << std::endl;
    for (int i = 0; i < 12; i++) {
        std::cout << (++c) << std::endl;
    }
}
```

### 13. 程序设计题

n 个人围成一圈，他们的编号一开始分别为1、2、...、n。从第一个人开始报数，数到 m 的人出列，再由下一个人重新从 1 开始报数，数到 m 的人再出圈，依次类推，直到所有的人都出圈。请利用`std::vector`和`iterator`设计程序，输出依次出圈人的编号。

● 输入描述：
输入两个整数 n，m。

● 输出描述：
输出一行 n个整数，按顺序输出每个出圈人的编号。

● 输入样例：
10 3

● 输出样例：
3 6 9 2 7 1 8 5 10 4

**参考答案**

```c++
#include <iostream>
#include <vector>

using namespace std;

int main() {
    int totalPeople;
    int target;
    vector<int> vec;
    cin >> totalPeople >> target;
    for (int i = 1; i <= totalPeople; i++) {
        vec.push_back(i);
    }
    int cur = 0;
    auto iter = vec.begin();
    while (vec.size() > 0) {
        if (++cur == target) {
            cout << *iter << " ";
            iter = vec.erase(iter);
            cur = 0;
        } else {
            ++iter;
        }
        if (iter == vec.end()) {
            iter = vec.begin();
        }
    }
}
```