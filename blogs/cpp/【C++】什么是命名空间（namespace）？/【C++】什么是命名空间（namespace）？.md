![7e0b73146cc8ebdd04ef16405a3d7f93.jpg](image/fbcfa1bd7d7866badd455662f1f13606966a1bbc21f7fd880dc043fd98695a27.awebp)

命名空间可以被理解为某种代码容器，帮助程序员将代码片段组织在不同的逻辑单元中，避免名称冲突，并使代码结构更加清晰。

# 全局命名空间

全局命名空间是程序中最基础的层级。在这个命名空间中定义的任何变量、函数、或其他类型可以在程序的任何其他地方直接访问（除非被局部命名空间或函数内的同名项覆盖）。

示例：

```c++
#include <iostream>

// 定义在全局命名空间中的函数
void sayHello() {
    std::cout << "Hello from Global Namespace!" << std::endl;
}

int main() {
    // 直接调用全局命名空间中的函数
    ::sayHello();
    return 0;
}
```

在这个例子中，`sayHello`函数定义在全局命名空间中，我们可以在`main`函数里直接调用它。

事实上，只需要一个函数在某个.cpp文件中被声明（而无需定义）在**全局作用域**当中，它就会被编译器视为处于全局命名空间！

```C++
// a.cpp
// 这里为了方便演示，直接在.cpp文件中加一个函数声明
// 在实际项目中（引用自其他代码文件的）函数声明一般会写在头文件中
void do_something();  

int main() {
    ::do_something();
}

// b.cpp
#include <iostream>

void do_something() {
    std::cout << "Hello World" << std::endl;
}
```

# 局部命名空间

命名空间也可以定义在一个局部范围内，或者嵌套在另一个命名空间中。这种方式常用于组织大型项目中的代码，使得不同的模块或库之间的命名不会发生冲突。

**示例**：

```c++
#include <iostream>

namespace myNamespace {
    // 定义在自定义命名空间中的函数
    void sayHello() {
        std::cout << "Hello from myNamespace!" << std::endl;
    }
}

int main() {
    // 调用全局命名空间中的函数（这个例子中没有定义，会导致编译错误）
    // sayHello();

    // 调用myNamespace命名空间中的函数
    myNamespace::sayHello();
    return 0;
}
```

在这个例子中，我们定义了一个名为`myNamespace`的命名空间，并在其中定义了一个`sayHello`函数。在`main`函数中，我们不能直接调用`sayHello`，因为它不在全局命名空间中。我们需要使用`myNamespace::sayHello()`来指明我们要调用的是哪个命名空间中的函数。

# 使用类/枚举类型模仿命名空间的行为

尽管**类不是命名空间**，你可以通过使用静态成员函数和静态数据成员来**让类在某种程度上模拟命名空间的行为**：

```cpp
#include <iostream>

class Utility {
public:
    static void printMessage(const std::string& message) {
        std::cout << message << std::endl;
    }
};

int main() {
    Utility::printMessage("Hello from Utility class with static method!");
    return 0;
}
```

在这个例子中，`Utility` 类使用了一个静态成员函数`printMessage`，这意味着你不需要创建`Utility`类的实例就可以调用这个方法。这使得`Utility`类在使用上类似于命名空间，但它仍然具有类的特性，比如访问控制。

类似地，作用域解析运算符（`::`）亦可作用于枚举类型（enumeration）。通过使用作用域解析运算符，程序员可以明确地指定某个枚举值所属的枚举类型，从而避免命名冲突。

示例：

```C++
#include <iostream>

enum Color : int {
    Red,
    Green,
    Blue
};

enum class State : int {
    Accpeted,
    Rejected,
    Pending
};

int main() {
    // 如果枚举类型未使用class关键字修饰，
    // 则其中的枚举常量会直接暴露到全局作用域当中
    // 此时访问这些枚举常量可使用::，也可以不使用
    Color color1 = Red;
    Color color2 = Color::Green;

    // 如果枚举类型被class关键字修饰，
    // 则必须通过::运算符访问其中的枚举常量，否则编译器报错！
    State state1 = State::Accpeted;

    //错误 C2065 “Rejected” : 未声明的标识符
    //State state2 = Rejected;
    
    // ...
    
    return 0;
}
```

# using namespace

`using namespace` 语句引入了一个命名空间中的所有名称（函数、变量、类型等），使它们在某个作用域（不会超出单个.cpp文件）中可用，无需命名空间前缀。这使得代码更简洁，但如果不小心使用，也可能导致名称冲突。

示例一：

```C++
int main() {
    std::cout << "Hello ";
    {
        std::cout << "hhh ";
        using namespace std;
        // 只在当前代码块作用域中，从"using namespace std"往下的地方生效！！！
        cout << "World" << endl;
    }
    std::cout << "Hello World" << std::endl;
    return 0;
}
```

示例二：

```C++
#include <iostream>

namespace First {
    void print() {
        std::cout << "Print from First namespace" << std::endl;
    }
}

namespace Second {
    void print() {
        std::cout << "Print from Second namespace" << std::endl;
    }
}


// 如果有一个处于全局命名空间的print函数，
// 那么main函数中调用 print() 将产生歧义错误，
// 因为编译器不清楚是调用 First::print 还是全局命名空间的print
// void print() {
//     std::cout << "Print" << std::endl;
// }

int main() {
    using namespace First;
    print();  // 这将调用 First::print()

    // 如果这里也使用 using namespace Second;
    // 那么调用 print() 将产生歧义错误，
    // 因为编译器不清楚是调用 First::print 还是 Second::print
    return 0;
}
```

# 显式提醒编译器使用全局命名空间中的变量/函数

在C++中，当你看到类似`::to_string()`这样的写法时，它的意思是在调用**全局命名空间**中的`to_string()`函数，而不是任何其他具有相同名字的局部或嵌套命名空间中的函数。

这种写法常用于以下几种情况：

1.  **防止命名冲突**：如果在你的程序或库中有其他同名的`to_string()`函数，使用`::to_string()`确保调用的是全局命名空间中的版本。
2.  **清晰表达意图**：明确表示函数来自全局命名空间，增加代码的可读性。

示例一：

```c++
#include <iostream>
#include <string>

using namespace std;

// 全局函数
string to_string(int value) {
    return "Global to_string: " + std::to_string(value);
}

class MyClass {
public:
    // 类成员函数，使用全局函数
    void print() {
        // 调用全局作用域的 to_string()
        cout << ::to_string(42) << endl; // 使用全局命名空间的 to_string
    }
};

int main() {
    MyClass myObject;
    myObject.print(); // 输出：Global to_string: 42
    return 0;
}
```

在这个例子中，`::to_string(42)` 调用的是全局命名空间中的 `to_string` 函数，而不是 `std::to_string`。输出结果将显示全局函数的结果。

示例二：

```c++
#include <iostream>
#include <string>

using namespace std;

// 全局函数
string to_string(double value) {
    return "Global to_string: " + std::to_string(value);
}

class MyClass {
public:
    // 类的成员函数
    string to_string(int value) {
        return "Class to_string: " + std::to_string(value);
    }
    
    void print() {
        cout << to_string(42) << endl;      // 调用类的成员函数
        cout << ::to_string(3.14) << endl;  // 调用全局函数
    }
};

int main() {
    MyClass myObject;
    myObject.print();
    return 0;
}
```

在这个例子中：

*   `MyClass` 中定义了一个 `to_string` 成员函数。
*   全局命名空间中存在一个程序员自定义的`to_string` 函数。
*   .cpp文件内部借助`using namespace std`引入了可不带`std::`前缀访问的`std::to_string`函数。

在 `print` 方法中：

*   `to_string(42)` 不加任何命名空间说明，**在类中编译器默认调用类的成员函数**。
*   `::to_string(3.14)` 调用的是全局命名空间中程序员自定义的 `string to_string(double value)` 函数。

示例三：

让我们对示例二稍作修改。

```C++
#include <iostream>
#include <string>

using namespace std;

class MyClass {
public:
    // 类的成员函数
    string to_string(int value) {
        return "Class to_string: " + std::to_string(value);
    }

    void print() {
        cout << to_string(42) << endl;      // 调用类的成员函数
        cout << ::to_string(3.14) << endl;  // 调用std::to_string函数
    }
};

int main() {
    MyClass myObject;
    myObject.print();
    return 0;
}
```

结合示例二和示例三，我们可以知道这里编译器在处理形如`::to_string(3.14)`的函数调用时，存在一个优先级关系——先看看全局命名空间中有无同名函数，如果没找到再尝试进入`using namespace`所引用的命名空间中查找。

示例四：

```C++
#include <iostream>

namespace First {
    void print() {
        std::cout << "Print from First namespace" << std::endl;
    }
}

void print() {
     std::cout << "Global Print" << std::endl;
}

int main() {
    using namespace First;
    
    // 错误 C2668 “print” : 对重载函数的调用不明确
    // print();
    
    // 显式调用全局命名空间中的print函数
    // 这样就不会让编译器产生歧义，程序可以正确通过编译并运行
    ::print();
    return 0;
}
```
