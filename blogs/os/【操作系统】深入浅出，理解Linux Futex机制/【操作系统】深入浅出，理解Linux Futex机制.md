![](image/eea0848602778ffea3b2242626832d79dd42bd1e9664d2c2e1fca643c7ab3f8e.awebp)

从Linux 2.5.7开始，操作系统内核提供了一个被称为Futex（Fast Userspace muTexes）的系统调用API。在此基础上，Linux平台的glibc库（GNU C Library）所提供的Pthread Mutex API在底层就是基于Futex实现的。

另外如果你有看过libstdc++（GNU C++ Standard Library）的[源码](https://github.com/gcc-mirror/gcc/blob/8c93a8aa67f12c8e03eb7fd90f671a03ae46935b/libstdc%2B%2B-v3/include/bits/std_mutex.h)，也能够注意到`std::mutex`本质上也不过只是对Pthread Mutex API进行的一层封装罢了。

可见，想要对Linux平台下线程互斥的底层原理有更深刻的把握，势必就需要理解Futex机制的工作原理。

在本文中，我将通过循序渐进、深入浅出的方式，从最原始的自旋锁设计出发，帮助你逐步理解Futex机制的来龙去脉和设计思想。

虽然我并不会在本文中直接去分析glibc和Linux内核中futex锁的实现源码，但我给出了非常详细的伪代码和注释（并且它们与真实实现已经足够贴近！），以及可供你直接编译调试的用户态手写代码。

相信你在读懂本文的基础上，再去自行学习真正的源码，一定会体验一把"畅通无阻"的快感。

# 0x01 引入：自旋锁

在刚学习《操作系统》这门课时，自旋锁肯定是我们最早接触到的概念。这种锁的特点在于如果某个进程申请占用锁失败，就会在原地自旋等待而不是主动释放CPU，直到下一次有机会抢占到锁。虽然用户态的自旋锁不会主动发起系统调用以将CPU让渡给其他进程，但其自选操作至少会白白浪费掉一个CPU时间片的时间。因此**在某个线程需要长时间占用自旋锁的情况下**，其效率是十分低下的。

以下是一个手写自旋锁的代码实例，其中内联汇编了x86-64架构提供的CAS指令。

对于对GCC内联汇编不熟悉的同学，我也给出了编译器根据内联汇编实际生成的汇编指令，以便对照。

```C++
#include <pthread.h>

#include <cstdint>
#include <cstdio>

class Atomic {
 public:
    /*
        The persude code of `CompareAndSwapInt32`:

        function CompareAndSwapInt32(dest, expected_value, new_value) {
            let old_value = *dest;
            if (*dest == expected_value) {
                *dest = new_value;
            }
            return old_value;        
        }
    */
    /*
        The disassembly code (with Intel style) of `CompareAndSwapInt32`:

        var_10= dword ptr -10h  // the offset of `exchange_value`
        var_C= dword ptr -0Ch  // the offset of `expected_value`
        var_8= qword ptr -8  // the offset of `dest`

        {
        // Save the function arguments from registers to stack.
        push    rbp
        mov     rbp, rsp
        mov     [rbp+var_8], rdi
        mov     [rbp+var_C], esi
        mov     [rbp+var_10], edx

        // Correspond to: "r" (exchange_value), "r" (dest), "a" (expected_value)
        mov     edx, [rbp+var_10]
        mov     rcx, [rbp+var_8]
        mov     eax, [rbp+var_C]

        // Correspond to: lock; cmpxchgl %1, (%2)
        lock cmpxchg [rcx], edx

        // Correspond to: "=a" (exchange_value)
        mov     [rbp+var_10], eax

        // Save the return value to eax register and return from the function.
        mov     eax, [rbp+var_10]
        pop     rbp
        retn
        }
    */
    static inline int32_t CompareAndSwapInt32(int32_t* dest, int32_t expected_value, int32_t exchange_value) {
        __asm__ volatile (
            "lock; cmpxchgl %1, (%2)"
            : "=a" (exchange_value)
            : "r" (exchange_value), "r" (dest), "a" (expected_value)
            : "cc", "memory"
        );
        return exchange_value;
    }
};

class MySpinLock {
 private:
    int32_t is_locked_;
 public:
    MySpinLock() : is_locked_(0) {}

    void Lock() {
        while (Atomic::CompareAndSwapInt32(&is_locked_, 0, 1) == 1) {}
    }
    
    void Unlock() {
        Atomic::CompareAndSwapInt32(&is_locked_, 1, 0);
    }
};

volatile int shared_count = 0;

MySpinLock my_spin_lock;

void* ThreadWorker(void* arg) {
    for (int i = 0; i < 10000; ++i) {
        my_spin_lock.Lock();
        shared_count += 1;
        my_spin_lock.Unlock();
    }
    return nullptr;
}

int main() {
    const int kNumThreads = 16;
    pthread_t threads[kNumThreads];

    for (int i = 0; i < kNumThreads; ++i) {
        pthread_create(&threads[i], nullptr, &ThreadWorker, nullptr);
    }

    for (int i = 0; i < kNumThreads; ++i) {
        pthread_join(threads[i], nullptr);
    }

    printf("The final value: %d\n", shared_count);
}

```

为了解决自旋锁过于浪费CPU时间的问题，有的资料中会提到如果某个线程抢占CPU失败，就让它sleep一段时间，睡醒了之后再继续抢。但是由于预测自旋锁被释放的时间是一件非常困难的事情，这种方法问题也存在着比较明显的问题。

# 0x02 尝试：纯用户态的mutex锁

为了解决自旋锁存在的问题，一个很自然的办法就是让当前没竞争到锁的线程先睡下去，并且将它们维护在一个等待队列当中。当锁被释放后，按一定的规则唤醒等待队列中的某一个线程，再让它抢占到锁即可。这就是mutex锁（互斥锁）的基本思想。

了解了mutex锁的基本概念之后，我们碰到的第一个问题就是：我们可以在纯用户态实现mutex锁吗？如果可以，这将是一个非常好的消息，因为我们不需要付出任何执行系统调用的开销。

为了回答这个问题，请看下面的**伪代码**：

```C
struct wait_entity {
    pid_t thread_id;
    struct list_head list_node;
}

struct mutex {
    bool is_locked;
    struct list_head wait_list;
    struct spinlock_t lock;  // 这个自旋锁用于保障lock/unlock操作的原子性
}

void do_mutex_lock(struct mutex* m) {
    spin_lock(&mutex->lock);
    
    // 1. 若锁已被其他线程占用，则让当前线程直接睡下。
    // 2. 若锁空闲则直接上锁，然后直接退出函数即可。
    if (m->is_locked) {
        // 将当前线程添加到等待队列
        struct wait_entity we = { gettid() };
        list_add_tail(&we->list_node, &mutex->wait_list);
        
        spin_unlock(&mutex->lock);
        
        // 执行pause系统调用，让当前线程睡下去
        pause();
    } else {
        m->is_locked = true;
        spin_unlock(&mutex->lock);
    }
}

void do_mutex_unlock(struct mutex* m) {
    spin_lock(&mutex->lock);

    // 解锁
    assert(m->is_locked == true);
    m->is_locked = false;

    // 如果等待队列不为空，就从其中取出一个任务予以唤醒。
    // 这里我们采用kill系统调用，向睡眠进程发送信号的方式来唤醒之
    if (!list_empty(&m->wait_list)) {
        struct wait_entity* we = pick_a_wait_entity(&m->wait_list);
        list_del(&we->list_node);
        kill(we->thread_id, SIGUSR1);
    }

    spin_unlock(&mutex->lock);
}
```

这段代码乍看上去似乎非常有道理，但倘若你仔细思考，就会发现它**其实是有问题的**。

设想如下的场景：

*   线程A调用`do_mutex_lock`函数，成功征用到mutex锁，进入临界区继续执行。
*   线程B调用`do_mutex_lock`函数，发现锁已被征用。然后它将自己添加到mutex锁的等待队列当中，并执行`spin_unlock(&mutex->lock);`以释放保护mutex锁的自旋锁。
*   操作系统接收到时钟中断，发生上下文切换。接下来CPU执行线程A。
*   线程A已经完成了临界区内的任务，接下去它会调用`do_mutex_unlock`函数以退出临界区。注意到此时保护锁`mutex->lock`已被线程B释放，故此时线程A可以畅通无阻地执行`do_mutex_unlock`中的代码。
*   接下来线程A注意到mutex锁的等待队列不为空（其中有线程B存在）。**注意，此时从线程A的视角来看，它会认为处于等待队列中的B已经真正睡下去了，因此会执行`kill`系统调用尝试将其唤醒！**
*   操作系统接收到时钟中断，发生上下文切换。接下来CPU执行线程B。
*   线程B执行`pause()`系统调用，然后真正睡下去。

在上述的情景中，我们看到线程A尝试唤醒线程B时，线程B实际上还未真正睡下，即A执行的是**虚假唤醒**。很显然，在这种情境下，线程B将永远沉睡下去而无法被唤醒！

从更深刻的角度来看，**虚假唤醒**的根源在于`do_mutex_lock`函数中释放保护自旋锁（`spin_unlock(&mutex->lock);`）和真正执行线程睡眠（`pause();`）这两个操作之间存在**窗口期**，因此给了线程A见缝插针的机会。

显而易见，我们无法将释放保护自旋锁的操作挪到真正执行线程睡眠操作的前面，否则会造成保护自旋锁的死锁。另一方面，Linux系统也没有向用户开放对线程状态进行更细粒度控制的API（我们后续将会看到内核态中如何通过对`task_struct`进行更细粒度的操作来消除虚假唤醒的问题）。

因此仅依赖用户态代码，我们是始终无法消除这个窗口期的。这也就是说，**我们无法实现纯用户态的mutex锁！**

# 0x03 解决：纯内核态的mutex锁

下面我们来分析在纯内核态中能否实现mutex锁。首先仍然请你自行阅读一下内核态mutex锁的**伪代码**：

```C
struct wait_entity {
    struct task_struct* task;
    struct list_head list_node;
}

struct mutex {
    bool is_locked;
    struct list_head wait_list;
    struct spinlock_t lock;  // 这个锁用于在内核态保障对is_locked和wait_list成员变量的操作的原子性
}

void do_mutex_lock(struct mutex* m) {
    spin_lock(&mutex->lock);
    
    // 1. 若锁已被其他线程占用，则让当前线程直接睡下。
    // 2. 若锁空闲则直接上锁，然后直接退出函数即可。
    if (m->is_locked) {
        // 将当前线程添加到等待队列
        struct wait_entity we = { current };
        list_add_tail(&we->list_node, &mutex->wait_list);
        
        // 将当前线程的状态修改为睡眠状态
        set_current_state(TASK_INTERRUPTIBLE);
        
        spin_unlock(&mutex->lock);
        
        // 调用schedule函数，该函数会完成如下几个步骤
        // 1. 因为当前线程已被修改为睡眠状态，故将其从调度器的就绪队列中移除
        // 2. 调度器从就绪队列中挑选出另外一个任务
        // 3. 执行系统上下文切换，CPU真正切换到被挑选出来的另一个任务并继续往下执行
        schedule();
    } else {
        m->is_locked = true;
        spin_unlock(&mutex->lock);
    }
}

void do_mutex_unlock(struct mutex* m) {
    spin_lock(&mutex->lock);

    // 解锁
    assert(m->is_locked == true);
    m->is_locked = false;

    // 如果等待队列不为空，就从其中取出一个任务予以唤醒。
    // 具体来说，就是：
    // 1. 将任务的状态修改为"可已正常被调度执行"，即`TASK_RUNNING`
    // 2. 将任务放回调度器的就绪队列当中去
    if (!list_empty(&m->wait_list)) {
        struct wait_entity* we = pick_a_wait_entity(&m->wait_list);
        list_del(&we->list_node);
        wake_up_process(we->task);
    }

    spin_unlock(&mutex->lock);
}
```

你不难注意到，内核态mutex锁的**伪代码**与刚才用户态的代码是十分像的，不过也稍许有些差异。这里我们主要需要关注的是**mutex锁已被其他线程征用**时的处理细节：

```C
    /* 内核态mutex锁 */
    if (m->is_locked) {
        // ...
        set_current_state(TASK_INTERRUPTIBLE);
        spin_unlock(&mutex->lock);
        schedule();
    }
    
    /* 用户态mutex锁 */
    if (m->is_locked) {
        // ...
        spin_unlock(&mutex->lock);
        pause();
```

可以看到，相较于用户态来说，内核态的mutex锁实现将**修改线程状态**（`set_current_state(TASK_INTERRUPTIBLE);`）和**真正将CPU转让给其他任务**（`schedule();`）拆分成了两步，且前者位于保护自旋锁所保护的临界区范围内。

那么，经过这种变化之后，内核态的mutex锁就能够避免虚假唤醒了吗？我们还是通过刚才的例子进行分析：

*   线程A调用`do_mutex_lock`函数，成功征用到mutex锁，进入临界区继续执行。
*   线程B调用`do_mutex_lock`函数，发现锁已被征用。
*   线程B将自己添加到mutex锁的等待队列当中，并将自己的状态修改为`TASK_INTERRUPTIBLE`。
*   线程B执行`spin_unlock(&mutex->lock);`，释放保护自旋锁。
*   操作系统接收到时钟中断，发生上下文切换。接下来CPU执行线程A。
*   线程A已经完成了临界区内的任务，接下去它会调用`do_mutex_unlock`函数以退出临界区。注意到此时保护锁`mutex->lock`已被线程B释放，故此时线程A可以畅通无阻地执行`do_mutex_unlock`中的代码。
*   接下来线程A注意到mutex锁的等待队列不为空（其中有线程B存在）。因此线程A会认为线程B已经真正睡下去了，它会调用`wake_up_process`内核函数尝试将其唤醒。
*   在`wake_up_process`内核函数中，线程B的状态被修改为`TASK_RUNNING`。
*   操作系统接收到时钟中断，发生上下文切换。接下来CPU执行线程B。
*   线程B执行`schedule()`内核函数。在该函数中，虽然线程B此时可能会被调度器换出，但**由于线程B的状态已变回`TASK_RUNNING`**，因此线程B并不会被调度器从其就绪队列中移除，即**稍后线程B又能继续正常地往下执行**。

由此可见，由于在退出保护临界区之前，线程B已经将自己的状态成功修改为了睡眠状态`TASK_INTERRUPTIBLE`，即使它并没有真正地执行上下文切换，对于稍后进入保护临界区的线程A来说，只要它调用`wake_up_process`内核函数将线程B的状态修改回来，线程B就不会在执行`schedule`内核函数之后真正睡下去（即不会从调度器的就绪队列中被移除出去）！

当然，到这里你仍然可能会有担忧：我们刚才的分析都是建立在内核所执行的实际调度动作（检查当前线程状态、换出当前线程、换入被选择执行的新线程等等...）是原子的假设之上的。假设它不是原子的，是否还会给线程A留下其他见缝插针的机会呢？

这个担心是大可不必的。首先，在Linux内核的源码中已经写明，在真正进行调度前会首先关闭当前CPU核的内核抢占功能：

```C
asmlinkage __visible void __sched schedule(void)
{
	struct task_struct *tsk = current;

	sched_submit_work(tsk);
	do {
          // 关闭当前CPU核的内核抢占功能，不允许更高优先级的任务抢占当前任务
		preempt_disable(); 
		__schedule(false);
		sched_preempt_enable_no_resched();
	} while (need_resched());
	sched_update_worker(tsk);
}
```

另外，从进一步被调用的`__schedule`函数的源码（如下，有删改）中可以看到，Linux内核在进行上下文切换前会关闭当前CPU核的中断响应，同时还有专门的自旋锁来保护当前CPU核的就绪队列。因此我们认为**Linux内核的实际调度动作是原子的**。

```C
static void __sched notrace __schedule(bool preempt)
{
	struct task_struct *prev, *next;
	struct rq_flags rf;
	struct rq *rq;
	int cpu;

	cpu = smp_processor_id();  // 获取当前CPU核的id
	rq = cpu_rq(cpu);  // 获取当前CPU核的就绪队列
	prev = rq->curr;  // 获取CPU核当前正在执行的任务

	local_irq_disable();  // 关闭当前CPU
	
    // ...
	
	rq_lock(rq, &rf);  // 给就绪队列上锁

    // ...
    
    // 如果当前任务的状态不为TASK_RUNNING（0x0000）
	if (!preempt && prev->state) {
        // 如果当前任务有信号待处理，则不能睡下。
        // 否则，将当前任务从就绪队列中移除，从而真正地睡下。
		if (signal_pending_state(prev->state, prev)) {
			prev->state = TASK_RUNNING;
		} else {
			deactivate_task(rq, prev, DEQUEUE_SLEEP | DEQUEUE_NOCLOCK);
            // ...
		}
	}

    // 让调度器挑选接下去准备执行的任务
	next = pick_next_task(rq, prev, &rf);
	
    // ...

    // 如果挑选出的任务不是当前任务，则执行上下文切换
    // 否则，退出__schedule函数并继续执行当前任务，不会发生上下文切换
	if (likely(prev != next)) {
		rq = context_switch(rq, prev, next, &rf);
	} else {
		rq_unlock_irq(rq, &rf);
	}
}
```

总而言之，现在我们可以得出结论：**在纯内核态我们的确可以实现mutex锁！**

# 0x04 优化：Futex——用户态+内核态实现mutex锁

## 理解基本思想

实际上，刚才介绍的内核态mutex锁已经可以落地使用了，但大佬们仍然观察到了其存在的不足：在现实场景中，其实大部分时候不会发生多线程竞争同一资源的情况。而内核态mutex锁要求每次申请锁核释放锁都需要陷入一次系统调用，这就显得比较浪费了。

因此，用户态+内核态配合实现的mutex锁——futex就孕育而生了。futex锁的关键点在于，将维护锁状态的任务完全放在用户态完成，而进程的睡眠（`futex_wait()`）和唤醒（`futex_wake()`）仍然放在内核态实现。通过用户态和内核态打配合的方式来完成加锁和解锁操作。

下面我们进一步来阐述这个配合到底是怎么打的。

以glibc中的futex锁实现为例，我们为futex锁定义三种状态：

*   0：锁没有被任何线程占用
*   1：锁被某个线程占用，同时没有任何其他线程想要获取锁
*   2：锁被某个线程占用，同时有其他的若干个线程想要获取锁

很显然，如果某段时间内只有单个线程想要进入临界区（即锁的状态始终在0和1之间切换），则该线程只需要简单地修改一下锁的状态就行了，而没有任何陷入系统调用的必要。

那对于更多线程同时想要抢占锁，会发生什么呢？

这里你先来看一个只含两个线程A和B的例子，直观理解一下：

*   线程A首先调用`lock()`，发现锁的状态为0，因此它直接在用户态将其修改为1，然后直接进入临界区执行。
*   线程B调用`lock()`，发现锁的状态为1，说明已经有人抢到锁了，因此它将状态修改为2，然后陷入系统调用`futex_wait()`让自己睡下去。
*   线程A完成临界区内的操作，调用`unlock()`退出临界区。具体来说：
    *   A将锁的状态置为0，表示现在锁暂时是空闲的了。
    *   A注意到锁原先的状态为2，说明刚才有其他线程也想抢占锁但没成功，现在已经在睡大觉了。因此A就需要执行`futex_wait()`，唤醒其中的一个（或多个）线程，让它（们）醒来再次尝试抢占锁。
*   线程B被唤醒，现在它发现锁的状态为0，因此立即抢占到锁并进入临界区执行。

现在相信你已经大致理解futex的工作机制了。不过在正式看我给你写好的伪代码之前，请你思考如下几个问题：

1.  刚刚的例子中只包含了两个线程，对于更多线程的情况，futex锁的代码应如何设计，才能正确工作？
2.  在(1)的前提条件下，为了确保futex锁正确工作，前例中的线程B应将锁的状态置为1还是2？
3.  Futex锁中使线程睡眠的效果需要通过陷入系统调用实现。它会出现类似于用户态mutex锁那样的虚假唤醒问题吗？

## 阅读伪代码

OK，现在你应该已经想得差不多了。你可以将我给你的**伪代码**与你的思考结果进行对照，看看哪里还有所欠缺。

另外值得一提的是，你可能注意到，这段伪代码中的用户态实现中，我并没有使用保护自旋锁之类的东西来保证对futex锁状态操作的原子性，而是使用一些原子指令直接对其进行操作。

事实上glibc中实际实现的futex锁采用的也是这种模式。这是因为对于这种简单的标志位更新操作，原子操作的性能是优于锁的。

至于这段基于原子操作的futex锁实现的线程安全性，则留作练习交给读者你自行完成了。同时在后文中，我也会给出在这段伪代码基础上真实可以运行的代码，以说明这段伪代码表述的算法流程的确是可行且正确的。

```C
typedef enum { F_FREE, F_SINGLE, F_COMPETITIVE } futex_state_t;


/*        用户态             */
struct futex {
    futex_state_t state;
}

void lock(struct futex* f) {
    // atomic_compare_and_swap(int* dest, int expect, int new)
    if (atomic_compare_and_swap(&f->state, F_FREE, F_SINGLE) != F_FREE) {
        while (atomic_exchange(&f->state, F_COMPETITIVE) != F_FREE) {
            // 系统调用sys_futex_wait(uintptr_t user_addr, int expect_value)
            // 假设在内核态中，操作系统真正使线程沉睡前，会首先检查*(int*)user_addr与expect_value是否相等
            // 如果不相等，则系统调用会直接返回，并不会真正使线程沉睡！
            syscall(sys_futex_wait, &f->state, F_COMPETITIVE);
        }
    }
}
 
void unlock(struct futex* f) {
    if (atomic_exchange(&f->state, F_FREE) == F_COMPETITIVE) {
        // 系统调用sys_futex_wake(uintptr_t user_addr, int wake_thread_num)
        // 第二个参数表示希望一次系唤醒的线程最大数目，一般直接取1就行。
        // 不然的话一次性唤醒多个线程去抢一把锁，没抢到的那些线程又要花费一次系统调用来再次睡眠，比较浪费。
        syscall(sys_futex_wake, &f->state, 1);
    }
}

/*        内核态                */
struct wait_entity {
    struct task_struct* task;
    struct list_head list_node;
};

struct wait_queue {
    struct spinlock_t lock;  // lock的作用同纯内核态版本的mutex锁
    struct list_head q;
}

// 这里wait_queue_map的功能类似于std::map
// 假如我们使用用户态futex结构体的地址来作为区分不同futex锁的唯一标志，
// 那么我们可以据此建立futex锁用户空间地址与其对应的等待队列的唯一映射关系。
struct wait_queue wait_queue_map[N];

// get_wait_queue_from_map是一个抽象函数，其功能为：
// 从wait_queue_map中获取到futex地址对应的等待队列
// 如果原先没有为当前futex锁分配等待队列，则自动在wait_queue_map为其分配一个
struct wait_queue* get_wait_queue_from_map(uintptr_t user_addr) {
    // 代码略...
}

// pick_one_from_wait_queue是一个抽象函数，其功能为：
// 按照某种规则从等待队列中挑出一项返回（但不会直接将该项从等待队列中移除）
struct wait_entity* pick_one_from_wait_queue(struct wait_queue* queue) {
    // 代码略...
}

// 对应系统调用sys_futex_wait
int do_futex_wait(uintptr_t user_addr, int expect_value) {
    futex_state_t state;
    
    get_user(state, user_addr);
    // 防止虚假唤醒！
    if (state != expect_value) {
        return -1;
    }
    
    struct wait_entity we = { current };
    struct wait_queue* queue = get_wait_queue_from_map(user_addr);
    
    spin_lock(&queue->lock);
    list_add_tail(&we->list, &queue->q);
    set_current_state(TASK_INTERRUPTIBLE);
    spin_unlock(&queue->lock);
    
    schedule();
    
    return 0;
}

// 对应系统调用sys_futex_wake
int do_futex_wake(uintptr_t user_addr, int wake_thread_num) {
    futex_state_t state;
    
    get_user(state, user_addr);
    if (state == F_COMPETITIVE) {
        return -1;
    }
    
    // 从wait_queue_map中取出当前futex锁对应的等待队列
    struct list_head* wait_queue = get_wait_queue_from_map(user_addr);
    spin_lock(&wait_queue->lock);
    
    while (!list_empty(wait_queue) && wake_thread_num > 0) {
        struct wait_entity* we = pick_one_from_wait_queue(wait_queue);
        wake_up_process(we->task);
        list_del(&we->list_node);
        
        --wake_thread_num;
    }
    
    spin_unlock(&wait_queue->lock);
    
    return 0;
}
```

## 手写代码环节

最后，在伪代码的基础上，我再给出一个可以实际运行的Futex锁用户态手写实现。

这里我直接调用了Linux系统已经封装好的futex系统调用。

```C++
#include <sys/syscall.h>
#include <linux/futex.h>
#include <syscall.h>
#include <unistd.h>
#include <pthread.h>

#include <cstdint>
#include <cstdio>
#include <array>
#include <iostream>

enum class FutexState : int32_t { kFree, kSingle, kCompetitive };

class Atomic {
 public:
    static inline int32_t CompareAndSwapInt32(int32_t* dest, int32_t expected_value, int32_t exchange_value) {
        __asm__ volatile (
            "lock; cmpxchgl %1, (%2)"
            : "=a" (exchange_value)
            : "r" (exchange_value), "r" (dest), "a" (expected_value)
            : "cc", "memory"
        );
        return exchange_value;
    }

    /*
        var_C= dword ptr -0Ch  // exchange_value
        var_8= qword ptr -8  // dest

        {
        // Save the function arguments from registers to stack.
        push    rbp
        mov     rbp, rsp
        mov     [rbp+var_8], rdi
        mov     [rbp+var_C], esi

        // Correspond to: `"0" (exchange_value), "m" (*dest)`
        mov     eax, [rbp+var_C]
        mov     rdx, [rbp+var_8]
        
        // Correspond to: `"lock; xchg %1, %2"`
        lock xchg eax, [rdx]
        
        // Correspond to: `"=r" (exchange_value)`
        mov     [rbp+var_C], eax
        
        mov     eax, [rbp+var_C]
        pop     rbp
        retn
        }
    */
    static inline int32_t Exchange(int32_t* dest, int32_t exchange_value) {
        __asm__ volatile (
            "lock; xchg %1, %2"
            : "=r" (exchange_value)
            : "0" (exchange_value), "m" (*dest)
            : "memory"
        );
        return exchange_value;
    }
};

class MyFutex {
 private:
    FutexState state_;

 public:
    MyFutex() : state_(FutexState::kFree) {}

    void Lock() {
        if (Atomic::CompareAndSwapInt32(
                reinterpret_cast<int32_t*>(&state_), 
                static_cast<int32_t>(FutexState::kFree), 
                static_cast<int32_t>(FutexState::kSingle)) 
            != static_cast<int32_t>(FutexState::kFree)
        ) {
            while (Atomic::Exchange(
                       reinterpret_cast<int32_t*>(&state_), 
                       static_cast<int32_t>(FutexState::kCompetitive)) 
                   != static_cast<int32_t>(FutexState::kFree)
            ) {
                FutexSyscall(FUTEX_WAIT, &state_, static_cast<int32_t>(FutexState::kCompetitive));
            }
        }
    }

    void Unlock() {
        if (Atomic::Exchange(
                reinterpret_cast<int32_t*>(&state_), 
                static_cast<int32_t>(FutexState::kFree)) 
            == static_cast<int32_t>(FutexState::kCompetitive)
        ) {
            FutexSyscall(FUTEX_WAKE, &state_, 1);
        }
    }

 private:
    int64_t FutexSyscall(int32_t op, FutexState* addr, int32_t argument) {    
        return static_cast<int64_t>(syscall(SYS_futex, addr, op, argument, nullptr));
    }
};

volatile int shared_count = 0;

MyFutex my_lock;

void* ThreadWorker(void*) {
    for (int i = 0; i < 10000; ++i) {
        my_lock.Lock();
        shared_count += 1;
        my_lock.Unlock();
    }
    return nullptr;
}

int main() {
    const int kNumThreads = 16;
    std::array<pthread_t, kNumThreads> threads;

    for (int i = 0; i < kNumThreads; ++i) {
        pthread_create(&threads[i], nullptr, &ThreadWorker, nullptr);
    }

    for (int i = 0; i < kNumThreads; ++i) {
        pthread_join(threads[i], nullptr);
    }

    std::cout << "The final value: " << shared_count << std::endl;
}

```

# 补充：排队自旋锁

在实际的自旋锁实现（如Linux内核）中，为了避免某个线程始终抢不到锁而出现饥饿，一般会采用一种叫"排队自旋锁"的设计，即先到先得——按顺序，先请求锁的线程先占用锁，后请求的线程后占用锁。

以下是一个手写排队自旋锁的示例：

```C++
#include <pthread.h>

#include <cstdint>
#include <cstdio>

class Atomic {
 public:
    static inline int32_t FetchAndAddInt32(int32_t* dest, int32_t value) {
        __asm__ volatile (
            "lock; xaddl %1, (%2)"
            : "=a" (value)
            : "a" (value), "r" (dest)
            : "cc", "memory"
        );
        return value;
    }
};

class MyTicketSpinLock {
 private:
    int32_t current_;
    int32_t ticket_;
 public:
    MyTicketSpinLock() : current_(0), ticket_(0) {}

    void Lock() {
        int32_t my_ticket = Atomic::FetchAndAddInt32(&ticket_, 1);
        while (my_ticket != current_) {}
    }
    
    void Unlock() {
        Atomic::FetchAndAddInt32(&current_, 1);
    }
};

volatile int shared_count = 0;

MyTicketSpinLock my_spin_lock;

void* ThreadWorker(void* arg) {
    for (int i = 0; i < 160000; ++i) {
        my_spin_lock.Lock();
        shared_count += 1;
        my_spin_lock.Unlock();
    }
    return nullptr;
}

int main() {
    const int kNumThreads = 8;
    pthread_t threads[kNumThreads];

    for (int i = 0; i < kNumThreads; ++i) {
        pthread_create(&threads[i], nullptr, &ThreadWorker, nullptr);
    }

    for (int i = 0; i < kNumThreads; ++i) {
        pthread_join(threads[i], nullptr);
    }

    printf("The final value: %d\n", shared_count);
}

```
