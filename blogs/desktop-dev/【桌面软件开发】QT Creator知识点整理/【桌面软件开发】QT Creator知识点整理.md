
![60467270_p0.webp](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c559bb4219b7435481488d86c55250b8~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1389&h=983&s=437514&e=webp&b=d9cfb5)

# 字符串处理

## 字符串的拼接与内插

示例如下：
```C++
// QString支持类似于std::string的字符串拼接操作
QString str1 = "Good morning! ";
QString str2 = str1 + "Hello" + " World";

// 字符串内插
QString i;           // current file's number
QString total;       // number of files to process
QString fileName;    // current file's name
QString status = QString("Processing file %1 of %2: %3")
                .arg(i).arg(total).arg(fileName);
```


# 信号槽

## 连接信号槽的各种方式

### 宏定义与函数指针式写法

通过以下的例子对比学习这两者的区别：

```C++
// 宏定义（无需显式指定信号和槽属于哪个类）
connect(this, SIGNAL(signal_dialog_send_msg(QString*)),
    parent, SLOT(slot_mainwindow_receive_msg(QString*)));
  
// 函数指针
connect(this, &Dialog::signal_dialog_send_msg, (MainWindow*)parent,
    &MainWindow::slot_mainwindow_receive_msg);
```

一般推荐使用函数指针的方式进行绑定，因为这种方式在底层基于C++编译器的模板推导实现，在槽函数（或信号）无重载的方式下，能够在编译阶段实现对槽函数、信号两者形参列表的一致性检测。

但对于槽函数（或信号）有重载的情况，在编译时QT并无法自动推导出应选取哪一个重载槽函数（信号）进行绑定，此时就需要程序员手工指定欲绑定的槽函数（信号）的签名，或者使用宏定义来使得代码更短一点：

```C++
// 假设MainWindow::slot_mainwindow_receive_msg有如下两个重载：
void MainWindow::slot_mainwindow_receive_msg(QString*)
void MainWindow::slot_mainwindow_receive_msg(QString*, int)

// 则绑定时必须指明函数签名
connect(this, &Dialog::signal_dialog_send_msg, (MainWindow*)parent,
    static_cast<void (MainWindow::*)(QString*)>(&MainWindow::slot_mainwindow_receive_msg));
    
// 使用宏定义的写法：
connect(this, SIGNAL(signal_dialog_send_msg(QString*)),
    parent, SLOT(slot_mainwindow_receive_msg(QString*)));
```

### lambda表达式

```C++
connect(this, &Dialog::signal_dialog_send_msg, [](QString* str) {
    qDebug() << "这是一个lambda表达式";
    qDebug() << *str;
});
```

### 设计界面"编辑信号/槽"模式进行连接

看如下的实例：

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/102c3b91cd554b6ba5ae1f43beb941cd~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=601&h=523&s=31110&e=png&b=2f3031)

在设计界面的"编辑信号/槽"编辑后.ui文件中出现如下内容：

```XML
 <connections>
  <connection>
   <sender>spinBox</sender>
   <signal>valueChanged(int)</signal>
   <receiver>progressBar</receiver>
   <slot>setValue(int)</slot>
   <!-- 后略... -->
```

在编译QT项目时生成的`ui_xxxx.h`文件中将自动包括真正实现连接的代码：

```C++
progressBar = new QProgressBar(centralwidget);
// ...
spinBox = new QSpinBox(centralwidget);
// ...
QObject::connect(spinBox, &QSpinBox::valueChanged, progressBar, &QProgressBar::setValue);
```

### 设计界面"转到槽"模式进行连接

这将会得到一个命名为`on_对象名_信号名`的槽函数，例如`void MainWindow::on_pushButton_clicked()`。QT在编译时将自动生成代码完成对应信号与这个槽函数的连接。

注意，若在创建槽函数后又在设计界面修改了QT对象的名称，QT Creator不会抛出任何提示，也不会自动修改槽函数的名称，且在编译时不会抛出任何错误提示！

# 对话框

## 模态对话框与非模态对话框

使用原生`QDialog`组件：

```C++
QDialog* myDialog = new QDialog(this);
QLabel* myLabel = new QLabel(myDialog);
myDialog->setWindowTitle("窗口标题");
myLabel->setText("窗口内容");

// 非模态对话框
myDialog->show();
qDebug() << "非模态对话框不会阻塞接下来代码的执行！";

// 模态对话框
myDialog->exec();
qDebug() << "模态对话框关闭后才会看到这行输出";
```

另外需要注意，由于C++中当函数退出时会立即自动销毁分配在栈上的C++对象，而非模态对话框又是不会阻塞函数运行的，因此若直接在栈上创建一个非模态对话框的对象并使用`show`方法显示，程序运行后会看到对话框一闪而过直接消失的现象：

```C++
void MainWindow::on_pushButton_clicked() {
    QDialog mydialog(this);
    mydialog.show();  // 非模态对话框一闪而过直接消失
    // mydialog.exec(); 非模态对话框不存在此问题
}
```

## 父子窗口通信

### 基于信号槽进行传值

请见如下实例：

**mainwindow.h**

```c++
#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QString>
#include "dialog.h"

namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
signals:
    void signal_mainwindow_send_msg(QString*);
public slots:
    void slot_dialog_closed(Dialog*);
    void slot_mainwindow_receive_msg(QString*);
private slots:
    void on_pushButton_clicked();
    void on_pushButton_sendMsg_clicked();
    void on_pushButton_clear_clicked();
private:
    Ui::MainWindow *ui;
};
#endif // MAINWINDOW_H
```

**dialog.h**

```c++
#ifndef DIALOG_H
#define DIALOG_H

#include <QWidget>
#include <QDialog>

namespace Ui {
class Dialog;
}

class Dialog : public QDialog {
    Q_OBJECT
public:
    explicit Dialog(QWidget *parent = nullptr);
    ~Dialog();
signals:
    void signal_dialog_closed(Dialog*);
    void signal_dialog_send_msg(QString*);
public slots:
    void slot_dialog_receive_msg(QString*);
private slots:
    void on_pushButton_clicked();
    void on_pushButton_2_clicked();
private:
    Ui::Dialog* ui;
    void closeEvent(QCloseEvent *event);
};
#endif // DIALOG_H
```

**mainwindow.cpp**

```c++
#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QDialog>
#include <QLabel>
#include <QMessageBox>
#include "dialog.h"

MainWindow::MainWindow(QWidget *parent) : QMainWindow(parent), ui(new Ui::MainWindow) {
    ui->setupUi(this);
    this->setWindowTitle("子窗口未开启");
}

MainWindow::~MainWindow() {
    delete ui;
}

void MainWindow::on_pushButton_clicked() {
    Dialog* myDialog = new Dialog(this);
    myDialog->show();
    this->setWindowTitle("子窗口已开启");
    ui->pushButton_sendMsg->setEnabled(true);
    ui->pushButton->setEnabled(false);
}

void MainWindow::slot_dialog_closed(Dialog* myDialog) {
    this->setWindowTitle("子窗口未开启");
    ui->pushButton->setEnabled(true);
    ui->pushButton_sendMsg->setEnabled(false);
}

void MainWindow::on_pushButton_sendMsg_clicked() {
    QString* msg = new QString(ui->lineEdit_toSub->text());
    emit signal_mainwindow_send_msg(msg);
}

void MainWindow::slot_mainwindow_receive_msg(QString* msg) {
    ui->lineEdit_fromSub->setText(*msg);
    delete msg;
}

void MainWindow::on_pushButton_clear_clicked() {
    ui->lineEdit_fromSub->clear();
}
```

**dialog.cpp**

```c++
#include "dialog.h"
#include "ui_dialog.h"
#include "mainwindow.h"

Dialog::Dialog(QWidget *parent) : QDialog(parent) {
    ui = new Ui::Dialog();
    ui->setupUi(this);
    /*
        这里注意一个小细节：QT连接信号槽时要求sender、receiver的类型
        必须分别与signal和receiver所属的类保持一致。
        因此这里parent必须先显式转换成MainWindow*类型，再进行信号槽连接，
        否则会编译错误！
    */
    connect(this, &Dialog::signal_dialog_closed,
            (MainWindow*)parent, &MainWindow::slot_dialog_closed);
    connect((MainWindow*)parent, &MainWindow::signal_mainwindow_send_msg,
            this, &Dialog::slot_dialog_receive_msg);
    connect(this, &Dialog::signal_dialog_send_msg,
            (MainWindow*)parent, &MainWindow::slot_mainwindow_receive_msg);
}

Dialog::~Dialog() {
    delete ui;
}

// 重载QWidget::closeEvent，使得对话框关闭（包括用户点右上角×的方式）时
// ，其能向父窗口发送消息。
void Dialog::closeEvent(QCloseEvent *event) {
    emit signal_dialog_closed(this);
}

void Dialog::on_pushButton_clicked() {
    this->QDialog::close();
}

void Dialog::slot_dialog_receive_msg(QString* msg) {
    ui->label->setText(*msg);
    delete msg;
}

void Dialog::on_pushButton_2_clicked() {
    QString* msg = new QString("这是一条来自子窗口的消息");
    emit signal_dialog_send_msg(msg);
}
```

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6978ea8185d944c095927cadf02f6839~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1073&h=637&s=38963&e=png&b=f0efef)

### 模态窗口传值

对于使用`int QDialog::exec()`方法弹出的模态对话框，当用户在该窗口内调用`void QDialog::accept()`、`QDialog::accept()`或`QDialog::done(int ret)`方法后，对话框会被系统自动关闭，同时父窗口得到exec方法的返回值。

若用户调用的是accept和reject方法，父窗口将分别得到整数`QDialog::Accepted=1`和`QDialog::Rejected=0`，而done方法则允许子窗口向父窗口传递用户自定义的状态码。

当然，用户在子窗口中调用`QWidget::close()`也不会出问题，此时父窗口将得到状态码0.

请看如下实例：

**dialog.cpp**

```C++
void Dialog::on_pushButton_clicked() {
    qDebug() << "Accept按钮被按下";
    accept();
}
void Dialog::on_pushButton_2_clicked() {
    qDebug() << "Done按钮被按下";
    done(2024);
}
void Dialog::on_pushButton_3_clicked() {
    qDebug() << "Reject按钮被按下";
    reject();
}
void Dialog::on_pushButton_4_clicked() {
    qDebug() << "Close按钮被按下";
    close();
}
```

**mainwindow.cpp**

```C++
void MainWindow::on_pushButton_clicked() {
    Dialog* mydialog = new Dialog(this);
    int ret = mydialog->exec();
    qDebug() << "父窗口接收到模态对话框的返回值：" << ret;
}
```

**输出：**

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/876a227e7caf4417be0878682993e737~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=345&h=196&s=18221&e=png&b=2e2f30)


## QT自带的消息弹窗

以下是一个实例。**进一步介绍参见书P54-55**.

```C++
int ret = QMessageBox::warning(this, "My Application",
    "The document has been modified.\nDo you want to save your changes?",
    QMessageBox::Save | QMessageBox::Discard | QMessageBox::Cancel,
    QMessageBox::Save);
// 函数的返回值即为用户在对话框中点击的按钮
switch (ret) {
    case QMessageBox::Save:
        qDebug() << "Save File";
        break;
    case QMessageBox::Discard:
        qDebug() << "Discard File";
        break;
    case QMessageBox::Cancel:
        qDebug() << "Cancel";
        break;
}
```

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e9ec1138b62441209e93dcf8bbfb0920~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=362&h=224&s=8116&e=png&b=f8f8f8)


# 资源

## 图片

### 加载图片并显示

直接从本地加载图片

```C++
QImage myimage;
// 注意，若加载图片失败，QT应用不会抛出任何错误！
myimage.load("C:/Users/Administrator/Desktop/favicon.png");
// 假设ui->icon是一个QLabel对象
ui->icon->setPixmap(QPixmap::fromImage(myimage));
// 函数运行结束后可直接销毁QImage对象，图片仍然能够正常显示在应用的界面上
```

从"资源"中加载图片

```C++
QPixmap pix = QPixmap(QString(":images/images/1.jpg"));
ui->icon->setPixmap(pix);
```

### 缩放图片

为了确保图片的大小与容器组件（一般为QLabel）相适应，需要调用`QPixmap::scaled(const QSize &size, Qt::AspectRatioMode aspectRatioMode`进行大小缩放。第二个参数的默认值为`Qt::IgnoreAspectRatio`，表示强制调整图片的宽高；若取`Qt::KeepAspectRatio`，则表示按比例调整到最大尺寸。

```C++
ui->label->setPixmap(pix.scaled(ui->label->size());
```

## 自定义菜单栏

如下图所示，通过QT Creator提供的图形化界面可以方便地创建和管理菜单栏。

并且在C++代码中可以通过`ui->menu_F`和`ui->action_O`之类形式可以直接访问到自定义菜单栏和菜单项。

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/2a11dd1880d5481ba69541a964db4028~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1681&h=782&s=107536&e=png&b=323334)

考虑到应用开发中可能有动态添加菜单的需求，给出纯代码实现如下：

```C++
MainWindow::MainWindow(QWidget *parent):
    QMainWindow(parent) , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    // 创建菜单栏
    QMenuBar *menuBar = this->menuBar();
    // 创建菜单
    QMenu *fileMenu = menuBar->addMenu("文件(&F)");
    QMenu *editMenu = menuBar->addMenu("编辑(&E)");
    QMenu *helpMenu = menuBar->addMenu("帮助(&H)");

    // 创建action并设置对应的快捷键
    QAction *newAction = new QAction("新建(&N)", this);
    QAction *openAction = new QAction("打开(&O)", this);

    // 为action设置icon
    QIcon iconNew(":images/image/new.png");
    QIcon iconOpen(":images/image/open.png");
    newAction->setIcon(iconNew);
    openAction->setIcon(iconOpen);

    // 为action设置快捷键
    // 注意，在Windows API中快捷键被称为accelerator（加速键）
    // 而在QT中，快捷键被称为shortcut
    newAction->setShortcut(QKeySequence("ctrl+n"));
    openAction->setShortcut(QKeySequence("ctrl+o"));

    // 将action添加到菜单
    fileMenu->addAction(newAction);
    fileMenu->addSeparator(); // 添加分隔符
    fileMenu->addAction(openAction);

    // 为action绑定动作
    connect(newAction, &QAction::triggered, []() {
        qDebug() << "Create New File!";
    });
    connect(openAction, &QAction::triggered, []() {
        qDebug() << "Open a File";
    });
}
```

## 自定义右键菜单

自定义右键菜单通过重载`QWidget::contextMenuEvent`实现。当用户在窗口中按下鼠标右键时，系统会自动调用这个函数。

例子如下：

```C++
void MainWindow::contextMenuEvent(QContextMenuEvent* event) {
    // 新建菜单
    QMenu* menu = new QMenu(this);

    // 创建菜单项并添加到菜单之中，写法与实现菜单栏完全一致
    QAction* action1 = new QAction("刷新\tF5", this);
    QAction* action2 = new QAction("关闭\tCtrl+E", this);
    menu->addAction(action1);
    menu->addAction(action2);

    // 为action绑定行为代码略...

    // 将菜单显示在用户鼠标所处的位置
    menu->exec(event->globalPos());
}
```

对于基于`QTextEdit`或`QPlainTextEdit`封装的控件类，在重载的`contextMenuEvent`方法中，还可以通过调用`createStandardContextMenu()`方法来替换上面代码中直接调用`new QMenu`的操作。这个方法创建一个标准的文本编辑框右键菜单，以供程序员进一步添加自定义菜单项或修改已有菜单项。

### 设置菜单项状态

- QAction::setEnabled(true)、QAction::isEnabled()
- QAction::setChecked(true)、QAction::isChecked()

## 自定义工具栏

自定义工具栏的方法与菜单栏非常相似。

```C++
/*
    创建一个工具栏对象，并添加到容器中。
    如果已在"设计"界面中添加了工具栏，则只需如下一句代码即可：
    QToolBar* toolBar = ui->toolBar;
*/
QToolBar* toolBar = new QToolBar(this);
this->addToolBar(toolBar);
    
// 创建一个工具栏选项并添加到工具栏中
QAction* tool1 = new QAction("新建");
toolBar->addAction(tool1);

// 创建一个字体选择器，并添加到工具栏中
toolBar->addWidget(fontSelector);
```

![image.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5fd0279d2063463e95ed007937197b70~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=420&h=135&s=10237&e=png&b=fafafa)

# 事件

- void mousePressEvent(QMouseEvent *event) override;

- void mouseMoveEvent(QMouseEvent *event) override;

- void mouseReleaseEvent(QMouseEvent *event) override;

- void mouseDoubleClickEvent(QMouseEvent *event) override;

- void keyPressEvent(QKeyEvent *event) override;

- void keyReleaseEvent(QKeyEvent *event) override;

## QMouseEvent

### 获取鼠标按下/松开事件

在重载的`mousePressEvent/mouseReleaseEvent`方法中，可以通过`event->button()`，来获取用户当前按下/松开了鼠标上的哪个键，从而导致了事件被触发。

```c++
void MainWindow::mousePressEvent(QMouseEvent *event) {
    auto button = event->button();
    if (button == Qt::LeftButton) qDebug() << "鼠标左键被按下！\n";
    if (button == Qt::MiddleButton) qDebug() << "鼠标中间滚轮被按下！\n";
    if (button == Qt::RightButton) qDebug() << "鼠标右键被按下！\n";
}
void MainWindow::mouseReleaseEvent(QMouseEvent *event) {
    auto button = event->button();
    if (button == Qt::LeftButton) qDebug() << "鼠标左键被松开！\n";
    if (button == Qt::MiddleButton) qDebug() << "鼠标中间滚轮被松开！\n";
    if (button == Qt::RightButton) qDebug() << "鼠标右键被松开！\n";
}
```

### 获取鼠标按键被按住的状态

在绘图软件需要用户持续按住鼠标按键并移动鼠标等特殊情景中，我们需要在`mouseMoveEvent`方法中检测鼠标的某个按键是否被按住。这可以通过`event->buttons()`来实现。

```C++
void MainWindow::mouseMoveEvent(QMouseEvent *event) {
    auto buttons = event->buttons();
    if (buttons & Qt::LeftButton) qDebug() << "鼠标左键被按住！\n";
    if (buttons & Qt::MiddleButton) qDebug() << "鼠标中间滚轮被按住！\n";
    if (buttons & Qt::RightButton) qDebug() << "鼠标右键被按住！\n";
}
```

### 获取鼠标的移动事件

在默认情况下，只有用户按住鼠标左/右键并移动，才会触发`mouseMoveEvent`事件。如果希望只是用户单纯地移动鼠标就能触发事件，则需要在对需要跟踪鼠标位置的组件，及其所属的各级父组件和容器，都调用`setMouseTracking(true)`。

例如：

```C++
MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    // do something...
    this->setMouseTracking(true);
    ui->centralwidget->setMouseTracking(true);
}
```

### 获取鼠标的位置

- `event->pos()`用于获取鼠标相对于窗口左上角的位置
- `event->globalPos()`用于获取鼠标相对于电脑屏幕左上角的位置

```C++
void MainWindow::mouseMoveEvent(QMouseEvent *event) {
    int posX = event->pos().x();
    int posY = event->pos().y();
    int posGlobalX = event->globalPos().x();
    int posGlobalY = event->globalPos().y();
    // do something...
}
```

注意，在用户按住鼠标并移动导致`mouseMoveEvent`事件触发的前提下，即使用户将鼠标移出窗口外，`event->pos()`依然可以返回正确的负值坐标。

### 检测修饰键是否被按下

有时候需要检测用户在执行鼠标动作的同时是否按下了键盘上的某个修饰键。这可以通过`event->modifiers()`实现。

```C++
void MainWindow::mousePressEvent(QMouseEvent *event) {
    auto modifiers = event->modifiers();
    if (modifiers & Qt::ControlModifier) qDebug() << "Ctrl被按下！\n";
    if (modifiers == Qt::AltModifier) qDebug() << "Alt被按下！\n";
    if (modifiers == Qt::ShiftModifier) qDebug() << "Shift被按下！\n";
}
```

注意，在QT中不支持在鼠标事件中检测用户在执行鼠标动作的同时是否按下了某个非修饰键的普通键盘按键。如有此类需求，需要自己手工重载`keyPressEvent` 和`keyReleaseEvent`以编写实现代码。

## QKeyEvent

### 捕获键盘按键按下/松开事件

使用`event->key()`，其返回值可能为`Qt::Key_A`、...、`Qt::Key_Z`、`Qt::Key_Up`、`Qt::Key_Left`、...

```C++
void MainWindow::keyPressEvent(QKeyEvent *event) {
    if (event->key() == Qt::Key_M && event->modifiers() & Qt::ControlModifier) {
        // do something...
    }
}
```

## QWheelEvent

### 捕获鼠标滚轮滚动事件

```C++
void MainWindow::wheelEvent(QWheelEvent *event) {
    int delta = event->angleDelta().y();
    if (delta > 0) {
        // 鼠标滚轮向上滚动...
    } else {
        // 鼠标滚轮向下滚动...
    }
}
```

# 各种控件

## QComboBox

- void setCurrentIndex(int index)
- void setCurrentText(const QString &text)
- int currentIndex() const
- QString currentText() const

## 输入框

### 类别

1.  QLineEdit：lineEdit是用于单行文本输入的控件，用户只能在单行中输入文本，通常用于需要用户输入少量文本的情况。**读写方法为text()/setText**。
1.  QPlainTextEdit：plainTextEdit是用于多行文本输入和显示的控件，用户可以输入和显示多行文本。同时这种控件一般出现于允许用户进行格式化和样式设置，如字体、大小等的场景。**读写方法为toPlainText/setPlainText**。
1.  QTextEdit：textEdit也是用于多行文本输入和显示的控件，和plainTextEdit类似，但还可以进行富文本编辑和显示，包括插入图片、超链接等功能。**读写方法为toPlainText/setPlainText**。

## QFontComboBox

QFont currentFont() const

QT控件可通过`void QWidget::setFont(const QFont &)`设置字体。

## QSpinBox

- QSpinBox::value()
- QSpinBox::setValue()

## 禁/启用输入控件

- QWidget::setEnabled(true)
- QWidget::setDisabled(true)
- QWidget::isEnabled()

# 绘图

## 触发重绘事件

首先在外部代码调用容器的`QWidget::update`以清除容器内绘制的内容并触发重绘事件。这会导致容器的`paintEvent`方法被调用，在该方法内绘图即可。

例子：

```C++
void MainWindow::mouseMoveEvent(QMouseEvent *event) {
    QPoint point = event->pos();
    cur_x = point.x();
    cur_y = point.y();
    if (canDraw && (event->buttons() & Qt::LeftButton)) {
        hasDrawed = true;
        pos_x = last_x;
        pos_y = last_y;
        width = cur_x - pos_x;
        height = cur_y - pos_y;
        update();
    }
}
void MainWindow::paintEvent(QPaintEvent *event) {
    if (hasDrawed) {
        QPainter painter(this);
        painter.drawRect(pos_x, pos_y, width, height);
    }
}
```

## 绘图函数

- QPainter::drawLine(int x1, int y1, int x2, int y2)
- QPainter::drawEllipse(int x, int y, int width, int height)
- QPainter::drawRect(int x, int y, int width, int height)
- QPainter::drawText(int x, int y, const QString &text)

## 设置画笔画刷

```C++
void MainWindow::paintEvent(QPaintEvent* evt) {
    QPainter painter(this);
    // 初始化画刷、画笔
    QBrush brush(Qt::SolidPattern);
    QPen pen(Qt::SolidLine);
    // 设置颜色
    pen.setColor(QColor(255, 0, 0));
    brush.setColor(QColor(255, 0, 0));
    // 设置画笔粗细
    pen.setWidth(3);
    // 选择画刷、画笔
    painter.setBrush(brush);
    painter.setPen(pen);
    // 绘图...
}
```

# 杂项

## 随机数

```C++
// 生成一个大小不定的随机正整数
int a = QRandomGenerator::global()->generate();
// 生成一个大小在[0, 5)范围内的随机正整数
int b = QRandomGenerator::global()->bounded(5);
```

## 定时器

```C++
Widget::Widget(QWidget *parent) : QWidget(parent) {
    this->timer = new QTimer(this);
    connect(this->timer, &QTimer::timeout,
            this, &Widget::slot_widget_timer_update);
}
void Widget::slot_widget_timer_update() {
    // 定时器触发，do something...
}
void Widget::on_pushButton_clicked() {
    timer->start(1000);  // 启动定时器，设置定时间隔为1000ms
}
void Widget::on_pushButton_2_clicked() {
    timer->stop();
}
```

## 获取系统时间

```C++
QDateTime time = QDateTime::currentDateTime();
QString str = time.toString("yyyy-MM-dd hh:mm:ss dddd");
```

## 状态栏

状态栏可在"设计"面板直接添加。

![image.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8a7d9ada9f8245f3a6096455dcb4b3e0~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=404&h=596&s=30059&e=png&b=333435)

如果需要更新状态栏中显示的内容，调用`QStatusBar::showMessage(const QString &message)`方法即可。

## 窗口最大化/最小化/正常化

- void QWidget::showMaximized()
- void QWidget::showMinimized()
- void QWidget::showNormal()

## 组件坐标/大小相关

### 获取组件坐标/大小

```C++
auto geometry = ui->plainTextEdit->frameGeometry();
qDebug() << QString("x=%1,y=%2")
                    .arg(geometry.x()).arg(geometry.y());
qDebug() << QString("w=%1,h=%2")
                    .arg(geometry.width()).arg(geometry.height());
```

### 设置组件坐标/大小

```C++
// 如果坐标大小都要设置，用setGeometry(QRect(x, y, width, height))
plainTextEdit->setGeometry(QRect(40, 40, 250, 140));

// 如果只是要重新调整大小，用resize(width, height)
plainTextEdit->resize(250, 140);

// 如果只是要重新调整坐标，用move(x, y)
plainTextEdit->move();
```

## 打开/保存文件交互窗口

例如如下：

```C++
bool MainWindow::on_actionOpen_triggered() {
    QString fileName = QFileDialog::getOpenFileName(
        this, "打开文档",
        QDir::homePath(), "文本文件 (*.txt);;所有文件 (*.*)"
    );
    if (!fileName.isEmpty()) {
        QFile file(fileName);
        if (file.open(QIODevice::ReadOnly)) {
            QTextStream in(&file);
            // 从文件中读取内容并显示在plainTextEdit上
            plainTextEdit->setPlainText(in.readAll());
            file.close();
            return true;
        } else {
            QMessageBox::critical(this, "错误", "打开文档失败！");
            return false;
        }
    } else {
        return false;
    }
}

bool MainWindow::on_actionsave_S_triggered() {
    QString fileName = QFileDialog::getSaveFileName(
        this, "保存文档",
        QDir::homePath(), "文本文件 (*.txt);;所有文件 (*.*)"
    );

    // 如果用户没有取消操作并指定了文件名
    if (!fileName.isEmpty()) {
        QFile file(fileName);
        if (file.open(QIODevice::WriteOnly)) {
            QTextStream out(&file);
            // 将plainTextEdit中的内容输出到out
            out << plainTextEdit->toPlainText();
            file.close();
            QMessageBox::information(this, "成功", "您已成功保存文档！");
            return true;
        } else {
            QMessageBox::critical(this, "错误", "保存文档失败！");
            return false;
        }
    } else {
        return false;
    }
}
```