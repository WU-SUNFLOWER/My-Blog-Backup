
![108320734_p0.jpg](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8a60131b8de442b0b5cd19cb2f0c7eb4~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=3880&h=1440&s=485424&e=jpg&b=f7f4f4)

本文用于记录笔者在学习「Windows API」时碰到的疑难点。本文对应的实验环境为Visual Studio 2022。

为了方便代码调试，我们首先编写一个自定义类，用于在VS的控制台中打印调试信息：

```c++
#include <sstream>

class MyDebugOutput {
private:
    std::stringstream stream;
public:
    ~MyDebugOutput() {
        OutputDebugString(stream.str().c_str());
    }
    template <typename T>
    MyDebugOutput& operator<<(const T& msg) {
        stream << msg;
        return *this;
    }
};
```

# 绘画相关

绘画的API比较简单，主要涉及到：①画什么图形; ②画图形的样式如何。

### 图形

这部分内容主要翻书P67~69。编写代码时需要注意明确**向API传入的坐标参数是否为相对于窗口用户区左上角的绝对坐标**。

- `MoveToEx(HDC hdc, int x, int y, LPPOINT lppt)`设定画笔的起始坐标。第四个参数为一`POINT`结构体指针，可供系统保存移动之前画笔的坐标，可以直接传nullptr。

- `LineTo(HDC hdc, int x, int y)`从画笔的起始坐标开始，到相对于用户区左上角的绝对坐标`(x, y)`画直线。

- `Ellipse(HDC hdc, int left, int top, int right, int bottom)`

- `Rectangle(HDC hdc, int left, int top, int right, int bottom)`

### 样式

样式涉及到HPEN和HBRUSH两个句柄。前者用于控制绘制图形的外轮廓，后者用于控制绘制图形的填充效果（可以类比ps里的油漆桶来理解）。

我们通过`HPEN CreatePen(int iStyle, int cWidth, COLORREF color)`来创建画笔句柄，该函数的三个参数分别为画笔的样式、宽度和颜色（通过RGB宏创建）。

画笔样式最常用的取值为`PS_SOLID`（实线）、`PS_DASH`（虚线）和`PS_DOT`（点线）。**这里需要注意，若想要绘制虚线或者点线，则画笔宽度`cWidth`的取值不能超过1，否则将看不到效果。**

至于填充画刷，最常用的为`CreateSolidBrush`（单一颜色的填充效果）和`CreateHatchBrush`（条纹线条填充效果，见书P66）。

此外，还可以通过`GetStockObject`函数获取系统自带的画刷样式，见书P65。

例子：

```C++
    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hDC = BeginPaint(hWnd, &ps);
        HPEN hPen = CreatePen(PS_DOT, 1, RGB(123, 123, 123));
        HBRUSH hBrush = CreateSolidBrush(RGB(233, 233, 233));
        SelectObject(hDC, hPen);
        SelectObject(hDC, hBrush);
        Rectangle(hDC, 10, 10, 500, 500);
        DeleteObject(hPen);
        DeleteObject(hBrush);
        EndPaint(hWnd, &ps);
        break;
    }
```

# 字体

### 设置字体与输出文字

字体这一块的API比较复杂。先来看看最基础的自定义输出字体并绘制到屏幕：

```C++
        HDC hDC = GetDC(hWnd);
        static char text[] = "Hello World";
        HFONT hFont = CreateFontA(
            100,  // cHeight 文字的高度
            0,    // cWidth 文字的宽度. 如取值为0则表示根据文字高度等比例自动缩放.
            0,    // cEscapement 每个文字相对于页底的角度，单位为0.1°.
            0,    // cOrientation 每个文字相对于页底的角度，单位为0.1°. 暂时没搞懂有什么用.
            0, // cWeight 字体粗细，取值0~1000. 0默认, 400正常,700粗体.
            true, // bItalic 是否启用斜体
            true, // bUnderline 是否启用下划线
            true, // bStrikeOut 是否启用删除线
            DEFAULT_CHARSET,    // iCharSet 字符集. 默认值1表示根据系统语言自动设置.
            OUT_DEFAULT_PRECIS, // iOutPrecision 输出精度. 默认值0
            CLIP_DEFAULT_PRECIS,// iClipPrecision 剪切精度. 默认值0
            DEFAULT_QUALITY,    // iQuality 输出质量. 默认值0
            FF_DONTCARE | DEFAULT_PITCH,  // iPitchAndFamily 字体的间距和系列. 默认值0
            "微软雅黑"  // pszFaceName 字体名称
        );
        SelectObject(hDC, hFont);
        // 绘制字体的左上角坐标为(100, 200)
        TextOutA(hDC, 100, 200, text, strlen(text));
        ReleaseDC(hWnd, hDC);
```

在此基础上，我们还可以设置绘制文字的颜色和背景色。这里我们直接对device context这个状态机进行操作即可，并不需要操作设置字体信息用的HFONT句柄：

```C++
SetBkColor(hDC, RGB(255, 0, 0));
SetTextColor(hDC, RGB(0, 255, 0));
```

### 获取字体和文本信息

为了获取当前字体的一些参数信息，以便我们自己编写的绘制代码可以正确计算某些坐标，需使用如下的函数：

```C++
TEXTMETRICA tm;
GetTextMetricsA(hdc, &tm);
```

其中TEXTMETRIC的内部结构如下：

```C++
struct tagTEXTMETRICW {
    LONG        tmHeight;  // 字符高度
    LONG        tmExternalLeading;  // 行间距
    LONG        tmAveCharWidth;  // 平均字符宽度
    LONG        tmMaxCharWidth;  // 最大字符宽度
    LONG        tmWeight;  // 字重
    BYTE        tmItalic;  // 是否斜体
    BYTE        tmUnderlined;  // 是否有下划线
    BYTE        tmStruckOut;  // 是否有删除线
    // 内容比较多,这里只展示几个最常用的字段...
}
```

此外，我们还希望得到：

①在当前文本行中，接下来输入文本的起始横坐标是多少; 

②当需要换行时，下一行文本的纵坐标是多少。

麻烦主要来自①：对于非等宽的字体，GetTextMetricsA只能告诉我们字符的平均宽度和最大宽度，因此我们仍然无法精确确定已有文本在屏幕上显示的宽度到底是多少。

幸运的是，GetTextExtentPoint32A函数可以帮助我们完成这项工作。

```C++
SIZE size;
// 传入已经绘制到屏幕上的字符串及其宽度即可
GetTextExtentPoint32A(hDC, text, strlen(text), &size);

// 接下来，如果我们希望在当前文本的后面继续在同一行显示文本
// 只需将size.cx作为绘制的起始坐标即可
TextOutA(hDC, size.cx, 0, text2, strlen(text2));

// 如果我们希望在当前文本的下一行显示文本（假设下一行是第二行）
// size.cy（或者tm.tmHeight）表示文本的行高，再加上行间距，
// 即可算出下一行文本的纵坐标.
TextOutA(hDC, 0, size.cy + tm.tmExternalLeading, text3, strlen(text));
```

# 动态效果

动态效果（动画）的实现依赖定时器：

```C++
    switch (message) {
        case WM_CREATE: {
            // SetTimer创建循环定时器
            // 第2~4个参数分别为Event ID, 定时器间隔(ms), 回调函数
            SetTimer(hWnd, 233, 33, nullptr);
            break;
        }
        // 循环定时器被触发，会向应用程序发送一个WM_TIMER消息
        case WM_TIMER:
            // 此时wParam的值即为触发WM_TIMER消息的定时器的Event ID
            // 可以据此针对不同的定时器执行不同的行为
            MyDebugOutput() << wParam;
            // do something...
            break;
        case WM_DESTROY:
            // 传入创建Timer时提供的Event ID，以销毁定时器
            KillTimer(hWnd, 233);
            PostQuitMessage(0);
            break;
    }
```

这里要注意一下，如果调用SetTimer的时候传入的回调函数为nullptr，在本质上等效于：

```C++
SetTimer(hWnd, 233, 33, [](HWND hWnd, UINT msg, UINT_PTR event_id, DWORD _) {
    // msg的取值恒为WM_TIMER
    // PostMessageA(HWND hWnd, UINT Msg, WPARAM wParam, LPARAM lParam);
    PostMessageA(hWnd, msg, event_id, 0);
});
```

也就是说，如果不传入回调函数，那么系统默认的行为就是触发WM_TIMER消息。

如果我们直接将定时器触发的逻辑直接写到回调函数里，就会覆盖系统的默认行为。例如下面这个定时刷新用户页面的例子：

```C++
SetTimer(hWnd, 233, 33, [](HWND hWnd, UINT msg, UINT_PTR id, DWORD _) {
    InvalidateRect(hWnd, nullptr, true);
}); 
```

**注意，经本人测试，如果要实现动画等动态效果，最好应将绘制的代码写在WM_PAINT中，然后通过在SetTimer函数中手工调用Invalidate的方法来重绘用户页面。如果将重绘的代码直接写在WM_TIMER里，可能会出现一些奇怪的问题。**

# WM_KEYDOWN与WM_CHAR

为了说明问题，我们先在`WndProc`中插入如下的代码：

```c++
        case WM_KEYDOWN: {
            MyDebugOutput() << "Here is WM_KEYDOWN, wParam=" << wParam << '\n';
            break;
        }
        case WM_CHAR: {
            MyDebugOutput() << "Here is WM_CHAR, wParam=" << wParam << '\n';
            break;
        }
```

当我先后在键盘上输入小写的`q`和大写的`Q`后，VS控制台的打印结果如下：

```python
Here is WM_KEYDOWN, wParam=81 #81对应大写字母Q的ASCII码
Here is WM_CHAR, wParam=113   #113对应小写字母q的ASCII码
Here is WM_KEYDOWN, wParam=16 #VK_SHIFT，用于输入大写字母Q
Here is WM_KEYDOWN, wParam=81
Here is WM_CHAR, wParam=81
```

我们注意到，对于输入字符（实际上可以是任何在ASCII码表中找到的可读字符或者控制符）的键盘操作，会先后触发`WM_KEYDOWM`和`WM_CHAR`。并且无论我实际想输入的是大写还是小写字母，接收`WM_KEYDOWN`消息时`wParam`参数的值都是对应**大写字母**的ASCII码。而在接下来接收`WM_CHAR`消息时，`wParam`参数中的值则根据大小写字母而有不同的取值。具体来说，按下键盘时默认输入的是小写字母，如果按住shift键再输入，或者开启了caps-lock键，那么在`WM_CHAR`里就会接收到大写字母。

另外通过这段输出，我们也可以知道对于`VK_SHIFT`等不存在于ASCII码表中的虚拟键，只能触发消息`WM_KEYDOWN`，`WM_CHAR`对此不会有任何响应。

# Shift/Ctrl组合快捷键问题

从上个问题中我们可以发现，对于用户敲击Shift键的动作，`WM_KEYDOWN`可以作出响应，而`WM_CHAR`却不然。那么假如我们的应用中，规定某个快捷键组合为`shift+q`，又该如何编写代码呢？

首先，根据前述的分析，我们肯定要将处理组合键的代码写在`WM_KEYDOWN`中。于是现在关键的问题就是如何检测用户在按住shift键的同时敲击了q键。

这里先揭晓答案，我们需要使用`short GetKeyState(int nVirtKey)`函数。根据微软官方的[文档](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate)"*If the high-order bit is 1, the key is down; otherwise, it is up.*"的说明，`GetKeyState`函数返回值中的最高位若为`1`，则表示对应的虚拟键被按下；若为`0`，则反之。

根据上面的分析，我们可以通过如下的代码实现Shift组合快捷键的检测：

``` c++
        case WM_KEYDOWN: {
            // 这里要注意WM_KEYDOWN里接收到的都是大写字母!
            if (wParam == 'Q') {
                // 掩码0x8000即0b1000_0000_0000_0000
                // 这里的按位与操作是为了提取short型返回值的最高位
                if (GetKeyState(VK_SHIFT) & 0x8000) {
                    MyDebugOutput() << "You hit shift+q!\n";
                }
                else {
                    MyDebugOutput() << "You hit q/Q!\n";
                }
            }
            break;
        }
```

经测试，代码可以输出正确的结果。当然，我们在编程时若不愿在我们的代码中留下`0x8000`这么一个奇怪的magic number，我们也可以将`GetKeyState`的返回结果与`0`作比较，因为C/C++中整型的最高位恰好也是符号位！

另外一个好消息是，对基于Ctrl组合键的检测，也可以使用上述代码实现，只需将代码中的`VK_SHIFT`替换成`VK_CONTROL`即可。

# 移动鼠标时检测鼠标被按住问题

在绘图程序等情景中，需要在`WM_MOUSEMOVE`中检测用户在移动鼠标的同时是否按住了鼠标左键。这可以通过检测`GetKeyState(VK_LBUTTON) < 0`来实现。

类似地，还可以检测用户是否按住右键（`VK_RBUTTON`）、鼠标中间滚轮（`VK_MBUTTON`）等。

# 获取鼠标坐标问题

为了获取鼠标的坐标，一种办法是使用`<windowsx.h>`头文件中的`GET_X_LPARAM`和`GET_Y_LPARAM`宏。

我们可以先看看怎么利用这两个宏编写代码，以实时获取鼠标的坐标。

```C++
    static int mousePosX = 0;
    static int mousePosY = 0;
    switch (message) {
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hDC = BeginPaint(hWnd, &ps);
            std::stringstream stream;
            // 利用字符串流拼接数据，并生成一个临时的字符串
            stream << mousePosX << ", " << mousePosY;
            std::string mystr = stream.str(); 
            TextOut(hDC, 0, 0, mystr.c_str(), strlen(mystr.c_str()));
            EndPaint(hWnd, &ps);
            break;
        }
        case WM_MOUSEMOVE: {
            mousePosX = GET_X_LPARAM(lParam);
            mousePosY = GET_Y_LPARAM(lParam);
            InvalidateRect(hWnd, nullptr, true);
            break;
        }
        // 后略...
    }
```

在这段代码中，当我们移动鼠标时，屏幕上实时地显示当前鼠标**相对于窗口用户区左上角**的坐标。

此外透过这两个宏的定义，我们也可以注意到接收`WM_MOUSEMOVE`消息时Windows系统是如何传递鼠标坐标的：

```c++
// 下面的代码仅代表在64位版本Windows系统中的情况：
#define GET_X_LPARAM(lParam) ((int)(short)((WORD)(((DWORD_PTR)(lParam)) & 0xffff)))
#define GET_Y_LPARAM(lParam) ((int)(short)((WORD)((((DWORD_PTR)(lParam)) >> 16) & 0xffff)))
```

可见在接收`WM_MOUSEMOVE`消息时，鼠标的相对坐标分别存放在`lParam`参数的高2Byte和低2Byte中。

另外，教材还为我们提供了另外一种获取鼠标相对坐标的方法：

```c++
case WM_MOUSEMOVE: {
    POINT point;
    // 获取鼠标相对电脑屏幕左上角的坐标，存入point中
    GetCursorPos(&point);
    // 将point中的坐标取出，换算成鼠标相对于
    // 窗口用户区左上角的坐标，再存回point中
    ScreenToClient(hWnd, &point);
    mousePosX = point.x;
    mousePosY = point.y;
    InvalidateRect(hWnd, nullptr, true);
    break;
}
```

经过测试，我们发现**这两种方法的效果是完全一致的**。那么什么时候该选用`GetCursorPos`和`ScreenToClient`函数来获取鼠标的坐标呢？一个简单的答案是，当我们需要在接收`WM_PAINT`或者其他消息时，需要根据用户当前的光标位置进行某些计算时，由于我们无法再通过`lParam`来实现，这时就只能使用这两个函数了。

# Caret问题

```c++
LRESULT CALLBACK WndProc(HWND hWnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    static char text[] = "Hello World";
    static int lineHeight;
    static int caretPosX = 0;
    static int caretPosY = 0;
    switch (message) {
        case WM_CREATE: {
            HDC hDC = GetDC(hWnd);
            TEXTMETRIC tm;
            // 获取文本的度量信息
            GetTextMetrics(hDC, &tm);
            // 计算行高
            lineHeight = tm.tmHeight + tm.tmExternalLeading;
            // 创建光标
            CreateCaret(hWnd, nullptr, 1, lineHeight);
            // 显示光标
            ShowCaret(hWnd);
            ReleaseDC(hWnd, hDC);
            break;
        }
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hDC = BeginPaint(hWnd, &ps);
            TextOut(hDC, 0, 0, text, strlen(text));
            TextOut(hDC, 0, lineHeight, text, strlen(text));

            SIZE size;
            GetTextExtentPoint(hDC, text, caretPosX, &size);
            
            // 设置光标位置
            SetCaretPos(size.cx, caretPosY * lineHeight);
            EndPaint(hWnd, &ps);
            break;
        }
        case WM_KEYDOWN: {
            switch (wParam) {
                case VK_LEFT: {
                    if (caretPosX > 0) --caretPosX;
                    break;
                }
                case VK_RIGHT: {
                    if (caretPosX < strlen(text)) ++caretPosX;
                    break;
                }
                case VK_UP: {
                    if (caretPosY > 0) --caretPosY;
                    break;
                }
                case VK_DOWN: {
                    if (caretPosY < 1) ++caretPosY; // 假定只有两行文本
                    break;
                }
            }
            InvalidateRect(hWnd, nullptr, true);
            break;
        }
        case WM_DESTROY:
            PostQuitMessage(0);
            break;
        default:
            return DefWindowProc(hWnd, message, wParam, lParam);
    }
    return 0;
}
```

# 禁（启）用菜单（项）问题

Windows API支持编写代码动态禁（启）用Menu Bar中的某个菜单（submenu），或者点开某个菜单后的某个菜单项（menu item）。

禁、启用操作对应的宏分别为`MF_DISABLED`、`MF_ENABLED`。

**禁用菜单项-代码示例：**

```c++
/* 写法一 */
HMENU hMenu = GetMenu(hWnd);
// 调用GetSubMenu函数获取特定菜单的句柄，
// 该函数的第二个参数表示目标菜单在Menu Bar中的位置（从0开始数）
HMENU hSubMenu = GetSubMenu(hMenu, 0);
// 宏MF_BYPOSITION表示调用EnableMenuItem时第二个参数的含义为
// 目标菜单项在菜单中的位置（从0开始数）
EnableMenuItem(hSubMenu, 1, MF_DISABLED | MF_BYPOSITION);

/* 写法二 */
HMENU hMenu = GetMenu(hWnd);
HMENU hSubMenu = GetSubMenu(hMenu, 0);
// 宏MF_BYCOMMAND表示函数第二个参数的含义为目标菜单项的ID号
EnableMenuItem(hSubMenu, IDM_EXIT, MF_DISABLED | MF_BYCOMMAND);

/* 写法三 */
HMENU hMenu = GetMenu(hWnd);
// 经测试，只要知道目标菜单项的ID号，在调用函数时直接传入hMenu句柄即可
EnableMenuItem(hMenu, IDM_EXIT, MF_DISABLED | MF_BYCOMMAND);
```

**禁用菜单-效果示例：**

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3540ab8814624a70a7792780da4ccae5~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=284&h=157&s=11084&e=png&b=faf9f9)

至于禁用菜单，写法与禁用菜单项基本一致，不过要注意两点：

1. 由于在Windows SDK中菜单并没有独立的ID号，因此只能通过指定位置的方式来对其进行操作。
2. 对菜单进行的操作最终需要反映到菜单栏上，因此需要调用`DrawMenuBar`函数来强制重绘菜单栏。

**禁用菜单-代码示例**

```c++
HMENU hMenu = GetMenu(hWnd);
EnableMenuItem(hMenu, 1, MF_DISABLED | MF_BYPOSITION);
DrawMenuBar(hWnd);
```

**禁用菜单-效果示例**


![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/3fbcfddc07ac4362ad3768e751b6f76d~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=204&h=81&s=5997&e=png&b=fefdfd)

# 插入菜单（项）问题

我们先来看插入菜单项的问题。

**插入菜单项-代码示例：**

```C++
HMENU hMenu = GetMenu(hWnd);
HMENU hSubMenu = GetSubMenu(hMenu, 0);
static char loadItemText[] = "导入(&L)";
MENUITEMINFOA menuInfo;

#define IDM_FILE_LOAD 233
        
// 字段cbSize必须设置为sizeof(MENUITEMINFO)
menuInfo.cbSize = sizeof(MENUITEMINFO);
// 字段fMask用于声明系统在创建菜单项时应读取结构体中的哪些字段
// MIIM_ID表示系统应读取字段wID
// MIIM_STRING表示应读取字段dwTypeData，且该指针指向一个字符串
menuInfo.fMask = MIIM_ID | MIIM_STRING;
// 字段wID用于设定菜单项的ID号
menuInfo.wID = IDM_FILE_LOAD;
// 字段dwTypeData指向资源的首地址
menuInfo.dwTypeData = reinterpret_cast<LPSTR>(loadItemText);
// 字段cch用于设定dwTypeData指向资源在内存中的长度
menuInfo.cch = strlen(menuInfo.dwTypeData);

// 写法一
// 第三个参数为true，表示将新的菜单项插入到菜单中的指定位置
// 原先位于该位置的菜单项及位居其后者，则顺次后移
InsertMenuItem(hSubMenu, 1, true, &menuInfo);

//写法二
// 第三个参数为false，表示将新的菜单插入到原先由第二个参数指定的菜单项的位置
// 同样地，原有的相关菜单项也会自动顺次后移
InsertMenuItem(hSubMenu, IDM_EXIT, false, &menuInfo);
```

**插入菜单项-效果示例：**

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ca93b6f48abf42d8ad457a27827cff5a~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=185&h=174&s=10997&e=png&b=f7f6f6)

与禁用菜单的问题类似，我们也可以将上述代码推广至"插入菜单问题"。

**插入菜单-代码示例**

```C++
// 获取菜单栏的句柄
HMENU hMenu = GetMenu(hWnd);
// 为准备要新插入的菜单创建句柄
HMENU hNewMenu = CreatePopupMenu();

static char loadItemText[] = "颜色(&C)";

MENUITEMINFOA menuInfo;
menuInfo.cbSize = sizeof(MENUITEMINFO);
// 宏MIIM_SUBMENU表示系统应读取字段hSubMenu，以将新菜单与其句柄绑定
menuInfo.fMask = MIIM_SUBMENU | MIIM_STRING;
menuInfo.hSubMenu = hNewMenu;
menuInfo.dwTypeData = reinterpret_cast<LPSTR>(loadItemText);
menuInfo.cch = strlen(menuInfo.dwTypeData);

// 将新的菜单插入到菜单栏上
InsertMenuItem(hMenu, 1, true, &menuInfo);
DrawMenuBar(hWnd);
```

**插入菜单-效果示例**

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ff913773e79e46b680c2f5ea88569917~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=218&h=74&s=6992&e=png&b=fefdfd)

# 追加菜单（项）问题

"追加菜单（项）问题"实际上是"插入菜单（项）问题"的一个子问题。显然，我们仍然可以使用`InsertMenuItem`函数来实现。当然，这就意味着我们需要创建一揽子繁琐的`MENUITEMINFOA`结构体。幸运的是，Windows SDK为我们提供了`AppendMenu`函数，来便捷地实现追加操作。

我们来看看如何向菜单栏追加一个菜单，并在这个菜单中添加若干个菜单项。

**追加菜单（项）-代码示例：**

```C++
// 获取窗口菜单栏的句柄
HMENU hMenu = GetMenu(hWnd);
// 为新追加的菜单创建句柄
HMENU hNewMenu = CreatePopupMenu();
static char loadItemText[] = "颜色(&C)";

#define IDM_COLOR_RED 101
#define IDM_COLOR_YELLOW 102
#define IDM_COLOR_GREEN 103

// 通过句柄，为新菜单追加菜单项
// 宏MF_STRING与AppendMenu第四个参数对应，表示菜单项作为一个字符串显示
// AppendMenu第三个参数即为菜单项的ID号
AppendMenu(hNewMenu, MF_STRING, IDM_COLOR_RED, "Red");
AppendMenu(hNewMenu, MF_STRING, IDM_COLOR_YELLOW, "Yellow");
AppendMenu(hNewMenu, MF_STRING, IDM_COLOR_GREEN, "Green");
        
// 将新菜单追加到菜单栏上
// 宏MF_POPUP用于声明要追加的资源是一个（弹出式）菜单，
// 并且此时第三个参数即为要追加菜单的句柄
AppendMenu(hMenu, MF_POPUP | MF_STRING, (UINT_PTR)hNewMenu, loadItemText);
DrawMenuBar(hWnd);
```

**追加菜单（项）-效果示例：**


![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4cd19970b42d4db9917b0e948c0fdd90~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=333&h=183&s=12435&e=png&b=fbfbfb)

# 勾选（撤销）菜单项问题

勾选菜单项通过`CheckMenuItem`函数实现。诚然，这个函数对菜单栏中的菜单本身并不会有任何效果。

在指定对哪个菜单项产生作用的问题上，`CheckMenuItem`函数与先前介绍的一系列函数存在着高度雷同，这里就不再赘述了。我们直接来看代码：

**勾选菜单项-代码示例：**

```C++
/* 写法一 */
CheckMenuItem(hMenu, IDM_COLOR_YELLOW, MF_CHECKED | MF_BYCOMMAND);

/* 写法二 */
CheckMenuItem(hNewMenu, 1, MF_CHECKED | MF_BYPOSITION);
```

**勾选菜单项-效果示例：**

![image.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/026c9bf465804ee99daad4ab437f054a~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=320&h=169&s=12621&e=png&b=fafafa)

与`EnableMenuItem`函数类似，`CheckMenuItem`函数也支持"反向操作"，即撤销对某个菜单项的勾选。我们只需要将前述代码中的宏`MF_CHECKED`替换为`MF_UNCHECKED`即可。

# 删除菜单（项）问题

删除菜单项一般可以通过`RemoveMenu`或者`DeleteMenu`函数实现。

与先前介绍的函数一样，它们同样支持`MF_BYCOMMAND`和`MF_BYPOSITION`模式，这里就不再赘述了。

当从菜单中移除菜单项时，这两个函数的执行效果一致。但当从菜单栏中移除菜单时，`RemoveMenu`函数只是将令目标菜单暂时不在菜单栏中显示了，后续还可通过该菜单的句柄再次动态地将其添加回菜单栏。而`RemoveMenu`除了在视觉意义上，将目标菜单从菜单栏中移除之外，还会自动释放目标菜单绑定的句柄（也就是说从内存中释放了目标菜单及其所有的菜单项），因此在此之后程序员就无法再对该菜单进行任何操作了。

```C++
HMENU hMenu = GetMenu(hWnd);
HMENU hNewMenu = CreatePopupMenu();
static char loadItemText[] = "颜色(&C)";

#define IDM_COLOR_RED 101
#define IDM_COLOR_YELLOW 102
#define IDM_COLOR_GREEN 103

AppendMenu(hNewMenu, MF_STRING, IDM_COLOR_RED, "Red");
AppendMenu(hNewMenu, MF_STRING, IDM_COLOR_YELLOW, "Yellow");
AppendMenu(hNewMenu, MF_STRING, IDM_COLOR_GREEN, "Green");
AppendMenu(hMenu, MF_POPUP | MF_STRING, (UINT_PTR)hNewMenu, loadItemText);

// 从菜单中移除菜单项
RemoveMenu(hMenu, IDM_COLOR_RED, MF_BYCOMMAND);
// 从窗口菜单栏中移除菜单
RemoveMenu(hMenu, 2, MF_BYPOSITION);
// 在内存中彻底销毁菜单句柄。
DeleteMenu(hMenu, 2, MF_BYPOSITION);
```

# 弹窗

## 模态对话框与非模态对话框

**非模态窗口**使用宏`CreateDialog(应用程序hInstance, MAKEINTRESOURCE(窗口资源ID号), 父窗口hWnd, 窗口处理函数)`创建。

对于非模态对话框，父窗口调用该宏后**将立即获得子窗口的HWND句柄**，即：

```C++
HWND hDialog = CreateDialog(hInst, 
                            MAKEINTRESOURCE(IDD_DIALOG), 
                            hWnd, 
                            DIALOG_Proc);
```

在开发过程中，若出现非模态对话框无法正常弹出的情况，请尝试在资源编辑界面将"可见"属性设置为true。

![无标题.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c8c18bac12b0445bbd05663d0944e44f~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=332&h=360&s=13386&e=png&b=262626)

**模态对话框**使用宏`DialogBox(hInstance, MAKEINTRESOURCE(窗口资源ID号), hWnd, 窗口处理函数)`创建。对于模态对话框，父窗口可以在子窗口关闭后接收到子窗口的返回值，即：

```c++
/* 子窗口 */
EndDialog(hDlg, ret_value);

/* 父窗口 */
int somevalue;
// 子窗口关闭后somevalue接收到返回值
somevalue = DialogBox(hInst, MAKEINTRESOURCE(IDD_DIALOG), hWnd, DIALOG_Proc);
```

## 子父窗口通信

子父窗口的通信通过宏`PostMessage(子/父窗口句柄, 消息号, wParam, lParam)`实现。此处"消息号"即为"WM_XXX"，Windows允许程序员自定义一个消息号并在父窗口的消息处理函数中实现处理自定义消息号的代码。

对于子窗口向父窗口发消息的情况，可以在子窗口的消息处理函数体内调用`GetParent(hDlg)`以得到父窗口句柄（其中`hDlg`为子窗口自己的句柄）。

这里需要注意，对于模态对话框，父窗口创建子窗口后，其当前正在执行的WndProc函数上下文会被阻塞，直至子窗口被关闭；但子窗口仍然可以通过向父窗口发送消息的方式，使得系统调用父窗口的WndProc函数，即系统仍可以创建另一个函数执行上下文。

# 捕获鼠标滚轮操作

```C++
case WM_MOUSEWHEEL: {
    // delta代表鼠标滚动滚动的增量，一般为120的倍数
    int delta = GET_WHEEL_DELTA_WPARAM(wParam);
    if (delta > 0) {
        // 鼠标滚轮向上滚动...
    } else {
        // 鼠标滚轮向下滚动...
    }
    break;
}
```

# 杂项

### 居中问题

要求利用`GetClientRect`函数对文本或者绘制出来的图形进行居中。这里以字符串为例：

```C++
SIZE size;
// 获取文本渲染到屏幕后的实际宽高
// 注意这里我们并不需要真的把文本绘制到屏幕上来获取数据，
// 只需提供待绘制的文本及其长度，该函数即可进行计算
GetTextExtentPoint32A(hDC, text, strlen(text), &size);

RECT rect;
// 获取窗口用户区的宽高
GetClientRect(hWnd, &rect);

// 计算待绘制的居中文本的实际坐标
int x = (rect.right - size.cx) / 2;
int y = (rect.bottom - size.cy) / 2;
TextOutA(hDC, x, y, text, strlen(text));
```

### 在弹出式菜单中添加分割线

使用宏`MF_SEPARATOR`

```C++
AppendMenuA(hNewMenu, MF_SEPARATOR, 0, nullptr);
```

### MessageBox

`MessageBox`可用于简单的**模态弹窗**。第4个参数可传`MB_OKCANCEL`（弹窗中包括"确定"和"取消"按钮）或`MB_OK`（弹窗中只有一个"确定"按钮）

```C++
int ret = MessageBoxA(hWnd, "你确定退出程序吗", "警告", MB_OKCANCEL);
if (ret == 1) {
    // 用户按下“确定 ”按钮
} else if (ret == 2) {
    // 用户按下“取消 ”按钮
} else {
    // ...
}
```

### Windows消息补充

- WM_LBUTTONDOWN, WM_LBUTTONUP（鼠标右键、中键与之类似）
- WM_MOUSEMOVE