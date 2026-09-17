# 04 · FreeRTOS 知识体系（我掌握了什么）

> 每个机制四段式：
>
> ```text
> 机制：      一句话说清它是什么（课程定义）
> 我的理解：  用自己的话讲原理（抄书的部分要标记）  ← 待你自己写
> 项目落点：  文件名 + 函数名 + 为什么这里要用它（不用会怎样）  ← 已按真实代码填
> 证据：      日志 / 截图 / 波形 / 实测数字
> ```
>
> 📌 2026-09-18：「项目落点」已从 bench 导入的 `firmware/my/demo` 回填（都是代码事实）；
> 「我的理解」和「证据」仍要你自己补——**能讲出来 + 拿得出，才算掌握**。
> 「自测问题」是尺子：答不上来就先别打勾。

---

## 1. 内核移植与配置

**机制**：把内核源码按目标架构接进来，靠 `port.c` 提供上下文切换与临界区实现。

- **我的理解**：待填
- **项目落点**（代码事实）：
  - 内核 V11.1.0，ARM_CM3 端口，`FreeRTOS/Src/port.c`
  - **中断安装用「向量表直连」**：`Core/Startup/startup_stm32f103rctx.s` L144/147/148 把 SVCall/PendSV/SysTick 指向 `vPortSVCHandler` / `xPortPendSVHandler` / `xPortSysTickHandler`
  - HAL 时基改到 TIM6，SysTick 完整让给内核：`Core/Src/stm32f1xx_hal_timebase_tim.c`
  - 优先级分组用 `NVIC_PRIORITYGROUP_4`（`Drivers/.../stm32f1xx_hal.c:157`），与 `configPRIO_BITS=4` 一致
- **证据**：`docs/evidence/20260918-vector-table/`（ELF 向量表实测：SVCall→0x080089e1、PendSV→0x08008c61、SysTick→0x08008ca9）

自测问题：

1. `PendSV` 为什么被选来做上下文切换？
2. `SysTick` 和 `configTICK_RATE_HZ=100` 是什么关系？tick 中断里做了哪些事？
3. `configMAX_SYSCALL_INTERRUPT_PRIORITY = 5<<4` 意味着优先级 0~4 的中断里**不能**调 FreeRTOS API，为什么？
4. CubeMX 生成的 `stm32f1xx_it.c` 里那几个空的 `SysTick_Handler` 为什么没被用上？

---

## 2. 任务管理

**机制**：任务是独立执行流，有自己的栈和优先级。

- **我的理解**：待填
- **项目落点**（`Core/Src/main.c` L134-137）：

| 任务 | 优先级 | 栈 | 职责 | 阻塞在 |
| --- | --- | --- | --- | --- |
| `vKeyTask` | 3 | 128 word / 512B | 10ms 扫 6 个按键，切面板/调参 | `vTaskDelay` |
| `vBuzzerTask` | 1 | 128 word | 按键音效 | 计数信号量 |
| `vLCDTask` | 1 | 256 word / 1KB | 事件组驱动重绘（9 个面板/标签） | 事件组 |
| `vLEDTask` | 0 | 128 word | 100ms 心跳闪灯 | `vTaskDelay` |
| 定时器服务任务 | 4 | 128 word | 内核自动创建（`configUSE_TIMERS=1`） | 定时器命令队列 |

- **证据**：任务创建代码；**运行时证据待补**（`vTaskList` 当前被 `configUSE_TRACE_FACILITY=0` 关掉了）

自测问题：

1. 任务栈分配在堆上还是静态区？由哪个宏决定？（本项目：动态，从 8KB 堆里切）
2. 4 个任务栈一共 2.5KB，加上 TCB / 队列 / 定时器，8KB 堆够吗？怎么验证？
3. 栈给太小会怎么表现？本项目为什么**查不出来**（`configCHECK_FOR_STACK_OVERFLOW=0`）？
4. 为什么按键任务优先级最高（3）？

---

## 3. 调度

**机制**：抢占式按优先级立即切换；同优先级可时间片轮转。

- **我的理解**：待填
- **项目落点**：`configUSE_PREEMPTION=1`、`configUSE_TIME_SLICING=1`；按键(3) 可抢占 LCD/Buzzer(1)；LED(0) 只在空闲前跑
- **证据**：待补（需要串口打印或 IO 翻转来证明抢占顺序）

自测问题：

1. 抢占式下，按键任务里如果去掉 `vTaskDelay`，会出现什么现象？
2. Buzzer 和 LCD 同为优先级 1，靠什么决定谁先跑？时间片的粒度是多少（tick = 10ms）？
3. `vTaskDelay(1)` 和 `vTaskDelayUntil()` 的区别？本项目按键轮询用哪个更合适？
4. `configMAX_PRIORITIES=5`，实际只用了 0/1/3/4，为什么这样反而好？

---

## 4. 堆内存管理

**机制**：内核自带 heap_1~heap_5 五种方案。

- **我的理解**：待填
- **项目落点**：**heap_4**（`FreeRTOS/Src/heap_4.c`）+ `configTOTAL_HEAP_SIZE = 8192`

| 方案 | 能否 free | 碎片 | 本项目 |
| --- | --- | --- | --- |
| heap_1 | 不能 | 无 | 未用 |
| heap_2 | 能 | 有 | 未用 |
| heap_3 | 能 | 依赖 libc | 未用 |
| heap_4 | 能 | 合并相邻空闲块 | ✅ **在用** |
| heap_5 | 能 | 同 heap_4 | 未用 |

- **证据**：待补（`xPortGetFreeHeapSize()` 打印、map 文件占用分析）

自测问题：

1. 8KB 堆是怎么分给 4 个任务 + TCB + 队列 + 定时器 + 邮箱的？算一遍。
2. 分配失败时 `pvPortMalloc` 返回什么？`configUSE_MALLOC_FAILED_HOOK=0` 的后果是什么？
3. 为什么选 heap_4 而不是 heap_2？（相邻空闲块合并）
4. 除了改 `configTOTAL_HEAP_SIZE`，还有什么降低占用的办法？（改小栈、用静态分配）

---

## 5. 任务间通信（队列 / 邮箱）

**机制**：队列是任务间数据通道，读写可阻塞；邮箱是长度 1 的队列。

- **我的理解**：待填
- **项目落点**：`App/dmm.c`
  - `xMailbox = xQueueCreate(1, sizeof(DMMData_t))`
  - ISR 侧 `xQueueOverwriteFromISR(xMailbox, &xDmmData, ...)`（新值覆盖旧值）
  - 任务侧 `xQueuePeek(xMailbox, &xResult, portMAX_DELAY)`（读而不取走，可重复读）
- **证据**：代码；待补实测（万用表读数变化）

自测问题：

1. 为什么万用表用**邮箱**而不是普通队列？（只要最新值，不要历史堆积）
2. `xQueuePeek` 和 `xQueueReceive` 的区别？这里为什么用 Peek？
3. 结构体是**按值拷贝**进队列的，`DMMData_t` 有多大？拷贝开销值得吗？
4. 从 ISR 里写队列为什么必须用 `FromISR` 版本？

---

## 6. 同步与互斥

**机制**：二进制信号量可同步/互斥，计数信号量可事件计数，互斥量带优先级继承。

- **我的理解**：待填
- **项目落点**：

| 机制 | 用在哪 | 为什么用它 | 不用会怎样 |
| --- | --- | --- | --- |
| 二进制信号量 | `lcd_task.c` `xSemaphoreForDMA` | SPI DMA 发完才拉高片选/继续下一次传输 | 屏幕数据错乱（片选提前释放） |
| 计数信号量 | `buzzer_task.c` `xSemaphoreCreateCounting(5, 0)` | 连按可积累请求，最多积压 5 次 | 用二进制信号量会丢按键音 |
| 互斥量 | 已开启（`configUSE_MUTEXES=1`）**但未使用** | — | — |

- **证据**：代码；待补（屏幕刷新的时序波形）

自测问题：

1. 二进制信号量做互斥和互斥量的区别是什么？（优先级继承）
2. 这个项目里有会出现优先级反转的共享资源吗？为什么暂时没暴露问题？
3. 蜂鸣器为什么用计数信号量而不是二进制信号量？
4. 中断里只能 `Give` 不能 `Take`，这个设计为什么反而好？

---

## 7. 中断与 ISR

**机制**：ISR 里只做最短的事，用 `FromISR` API 通知任务。

- **我的理解**：待填
- **项目落点**（中断 → 任务 的完整解耦链）：

| 中断源 | NVIC 优先级 | ISR 里做了什么 | 通知了谁 |
| --- | --- | --- | --- |
| EXTI3（PA3 触发） | 5 | 关自己中断 → 启动 ADC DMA → 启动 Hold-Off 定时器 → 复位 Force Trigger | 软定时器 |
| DMA1_Ch1（ADC 常规完成） | 6 | 换算 1024 点波形 → `xEventGroupSetBitsFromISR(WAVEFORM_PANEL_REPAINT_BIT)` | LCD 任务 |
| ADC1_2（注入完成） | — | 算 VDDA/万用表/电源/触发电压 → 覆盖邮箱 → `SetBitsFromISR(PWR|DMM 重绘位)` | LCD 任务 |
| DMA1_Ch3（SPI1 TX 完成） | 6 | `xSemaphoreGiveFromISR(xSemaphoreForDMA)` | LCD 任务 |
| DMA2_Ch3（DAC） | **0** | 无 FreeRTOS 调用 | — |
| TIM6（HAL 时基） | — | `HAL_IncTick()` | — |

- **证据**：代码 + `docs/evidence/20260918-vector-table/`；⚠️ 见 `docs/02` 关于 DMA2_Ch3 优先级 0 的隐患

自测问题：

1. `xHigherPriorityTaskWoken` 和 `portYIELD_FROM_ISR` 配合起来做了什么？漏掉会怎样？
2. 为什么优先级 0 的中断里**不能**调用 `xQueueOverwriteFromISR`？
3. 采样为什么不在中断里直接画波形？（1024 点换算 + SPI 传输的时间）
4. 触发为什么要在 ISR 里「先关自己的中断」？

---

## 8. 软件定时器

**机制**：由定时器服务任务统一管理，回调运行在服务任务上下文。

- **我的理解**：待填
- **项目落点**：`App/waveform_capture.c`
  - `xHoldOffTimer`：10ms **单次**，回调里清 EXTI 标志 + 重新使能中断（防止触发抖动反复采集）
  - `xForceTriggerTimer`：100ms **周期**，回调里 `__HAL_GPIO_EXTI_GENERATE_SWIT` 软触发（保证无信号时屏幕也有刷新）
  - ISR 里用 `xTimerStartFromISR` / `xTimerResetFromISR`
- **证据**：代码；定时器服务任务优先级 4（`configTIMER_TASK_PRIORITY = MAX-1`）

自测问题：

1. 定时器回调里能不能阻塞/`vTaskDelay`？为什么？
2. 定时器服务任务优先级是 4（比所有任务都高），配这么高会有什么影响？
3. 为什么 Hold-Off 用单次定时器而 Force Trigger 用周期定时器？
4. 软定时器的精度受什么影响？（tick = 10ms，所以 10ms 级别的定时本身就贴着 tick 粒度）

---

## 9. 观测与调试 ⚠️ 本项目最薄弱的一环

**机制**：栈水位、堆余量、任务状态、CPU 占用是判断系统健康度的四个指标。

- **我的理解**：待填
- **项目落点**：**当前一个都没开**
  - `configCHECK_FOR_STACK_OVERFLOW = 0`
  - `INCLUDE_uxTaskGetStackHighWaterMark = 0`
  - `configGENERATE_RUN_TIME_STATS = 0`
  - `configUSE_TRACE_FACILITY = 0`（所以 `vTaskList` 也用不了）
- **证据**：无 → **这就是下一步最该补的**

自测问题：

1. 打开上面四个宏分别要改哪里？会带来多少额外 RAM/ROM 开销？
2. 栈水位是「历史最小剩余」，怎么用它反推每个任务该给多大栈？
3. 任务卡死时（饥饿/死锁），有哪些手段定位？
4. 「能用调试器单步」和「能观测运行时指标」是两回事，为什么后者更重要？

---

## 10. 应用层 · 成品（示波器 + 数字万用表 + 信号发生器）

**机制**：ADC 采样 + DMA 搬运 + 任务处理 + LCD 显示，构成「采集—处理—显示」流水线。

- **我的理解**：待填
- **项目落点**：
  - 示波器：`waveform_capture.c`（TIM3 触发 + ADC 常规序列 + DMA + EXTI3 边沿触发 + Hold-Off）
  - 万用表：`dmm.c`（TIM2 触发 ADC 注入序列 + 挡位 GPIO + VREFINT 校准 + 邮箱）
  - 信号发生器：`waveform_generator.c`（DAC + DMA + TIM5，正弦/三角/方波）
  - 显示：`lcd_task.c` + `App/GUI/*`（事件组按位重绘）
- **证据**：`docs/05` 功能表；**实测指标待补**

自测问题：

1. 采样率 128.1kSa/s 是怎么算出来的？受 ADC 时钟、采样时间、DMA 哪个环节限制？
2. 1024 点缓冲为什么要用 DMA 而不是查询/中断逐点？
3. 边沿触发在软件里怎么实现？Hold-Off 和 Force Trigger 各解决什么问题？
4. 时基切换时采样率和显示怎么配合？（`SetSampleRate` + `GetSampleRate` 反算）
5. 万用表的 ADC 值怎么换算成物理量？VREFINT 校准解决的是哪部分误差？
6. 三种功能共用 ADC1/DMA/LCD，切换时为什么不会互相踩？

---

## 待补

- [ ] 每个机制的「我的理解」用自己的话补齐（不许抄书）
- [ ] 第 9 节：打开观测宏，把栈水位/堆余量/CPU 占用变成真实数字
- [ ] 把 `docs/03` 里的 🟡 逐条升级为 ✅
