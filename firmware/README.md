# firmware · 代码归档

> 这一层放**代码**，并且严格区分来源。记录仓库的价值在于「哪段是我写的」，混在一起就说不清了。

## 目录

```text
firmware/
├── my/
│   └── demo/          # 成品工程（STM32CubeIDE），2026-09-18 从 bench 导入
├── course-reference/  # 课程配套源码（⚠️ 版权：已移出公开仓，见下方私有仓链接）
└── README.md
```

## `my/demo` 是什么

| 项 | 值 |
| --- | --- |
| 来源 | bench：`D:\Project\FreeRTOS Worksapce\demo` |
| 导入日期 | 2026-09-18 |
| IDE | STM32CubeIDE（`.project` / `.cproject` / `.ioc` / `.launch`） |
| 规模 | 187 个文件，约 7.4 MB |
| 排除内容 | `Debug/`（42MB 编译产物，含 `demo.elf` / `.map`，未入库） |
| 内核 | FreeRTOS V11.1.0（`FreeRTOS/`），heap_4 |
| 应用层 | `App/`：`dmm.c`（万用表）、`waveform_capture.c`（示波器采集）、`waveform_generator.c`（信号发生器）、`Drivers/`、`GUI/`、`Tasks/` |

工程结构与关键配置见 `docs/02-开发环境.md`，功能实现见 `docs/05-成品功能与实现.md`。

> `Debug/` 被排除是**有意的**：编译产物不该进 Git。需要的话可以重新构建（`make -C firmware/my/demo/Debug` 或直接用 CubeIDE）。
> 但注意 `Debug/demo.map` 和 `demo.elf` 在这次核对里起过关键作用（验证中断向量表），相关结论已存进 `docs/evidence/`。

## ⚠️ 待确认：源码归属

导入的代码里，几乎所有文件头都写着：

```c
/*
 * dmm.c
 *  Created on: Apr  5, 2026
 *      Author: liuyu
 */
```

`liuyu` 是课程模板/示例工程里的作者标记（`App/Drivers/lcd.a` 这个预编译 LCD 库也是同一个作者）。**这意味着现在无法仅凭文件头区分「我写的」和「照课程模板/配套源码来的」。**

这件事必须确认清楚，因为它直接决定：

1. `docs/03-学习进度.md` 里「我的实现」的可信度；
2. 简历里这些模块能不能写成「我实现的」；
3. 面试被追问「这段为什么这么写」时你能不能接住。

**确认方式（任选）**：

- 回忆并按模块标注：哪些是跟着视频一行行敲的、哪些是直接拿模板改的；
- 看 Git/IDE 的本地历史（本工程**没有** `.git`，只有 Eclipse 的 `.settings`）；
- 找出课程资料里的原始工程做 diff（课程资料里的 `配套源码持续更新~` 目前只到 `p1.2`，后续章节的源码需要从付费资料里找）。

确认后请把结论写在本文件下方，并在 `docs/03` 的对应行注明。

### 归属结论（2026-09-18 完成；**2026-09-18 晚已用课程原码 diff 复核并更正**）

> ✅ **已取得课程配套源码并完成逐文件 diff**（bench 开机后从
> `D:\BaiduNetdiskDownload\FreeRTOS课程资料\配套源码持续更新~` 解压 19 个 example，
> 并找到基础模板 `D:\Project\FreeRTOS Worksapce\freertos_hal_template`）。
> **前一版基于"代码取证"的结论中，「按键驱动最可能照抄」一条已被证伪，见下方更正。**

#### 🔴 决定性证据：课程源码里没有你的代码

| 对比项 | 结果 |
| --- | --- |
| 课程配套源码（19 个 example，非库 `.c/.h`） | **207 个文件** |
| 你的 `App/` 层 | **48 个文件** |
| 两边**同名**文件 | **4 个**（`key.c`、`key.h`、`key_task.c`、`key_task.h`） |
| 同名文件中**逐字节完全一致**的 | **0 个** |
| 你的 `key.c` 时间 vs 课程 `key.c` | **2026-03-21** vs **2026-06-26**（你的早 **3 个月**） |

**关键点**：
1. 课程基础模板 `freertos_hal_template` **只有 `Core/`、`Drivers/`、`FreeRTOS/`，没有 `App/` 目录** → `App/` 这一层是你的。
2. 课程 19 个 example 中**只有 4 个含应用代码**：`3.1 example2`（`test.c`）、`3.1 example4`（`led1.c`）、`p1.1`/`p1.2`（`key_task.c` / `key.c`）。**没有任何一个涉及 GUI、万用表、示波器、信号发生器**。
3. 同名的那 4 个文件，**内容都不同**，且你的版本更早、更抽象。以 `key.c` 为例：

| | 课程 `p1.2/Drivers/key.c` | 你的 `App/Drivers/key.c` |
| --- | --- | --- |
| 结构体 | `KeyHandle_TypeDef`，内联 `GPIO_Port`/`GPIO_Pin` | `Key_HandleTypeDef` + `Key_InitTypeDef`，**回调式** |
| 读引脚 | 直接 `HAL_GPIO_ReadPin(Handle->GPIO_Port, ...)` | 调 `Handle->Init.ReadPinCallback()` |
| 引脚依赖 | 驱动内写死，一个按键一个实例 | 驱动**不知道引脚**，6 个按键共用一份代码 |

→ 你把课程的直接读引脚版本**重构成了回调式**，这是为了复用出 6 个按键实例（对应 `docs/03` 第 19 条「一份 `Key_Scan()` 复用出 6 个实例」）。

#### 更正说明

前一版结论里「`p1.1`/`p1.2` 在免费源码范围内，**最可能照抄**，建议面试验证时重点自证」——
**该判断已被证伪，撤回**。事实相反：课程原码比你的代码晚 3 个月，且你的实现更抽象。这两章不但不是照抄，反而是**你主动重构课程示例**的证据。

#### 复核后的逐模块归属

| 模块 | 文件 | 判定 | 依据 |
| --- | --- | --- | --- |
| **LCD 预编译库** | `App/Drivers/lcd.a` + `lcd.h` | **课程提供（二进制）** | 符号表含 `lcd.c`/`lcd_default_font.o`；**非你编写** |
| 按键通用驱动 | `App/Drivers/key.c/.h` | **你重构**（课程有对应版本，你改成回调式） | 同名不同内容；你的早 3 个月；结构改为回调 |
| 按键任务 | `App/Tasks/key_task.c/.h` | **你重构** | 同上；课程版在 `User/Task/`，你归入 `App/Tasks/` |
| 按键实例 | `App/Tasks/Keys/key1..4/up/down.c` | **你编写** | 课程无此设计（课程只有一个 `key_task.c`）；6 实例复用是你引入的 |
| 万用表 | `App/dmm.c` | **你编写** | 课程 19 个 example 中无对应代码、无同名文件 |
| 示波器采集 | `App/waveform_capture.c` | **你编写** | 同上 |
| 信号发生器 | `App/waveform_generator.c` | **你编写** | 同上 |
| GUI 面板 | `App/GUI/*`（13 文件） | **你编写** | 课程无任何 GUI 代码 |
| 任务框架 | `Core/Src/main.c` L131-138 | 你在模板基础上编写 | 模板无 `App/`、无任务创建代码 |
| 三合一集成 | 事件组/邮箱/信号量串联四个仪器 | **你设计** | 课程无此成品；`docs/05` 数据流图即你的设计 |

**总结论**：除课程提供的预编译 LCD 库外，**`App/` 层全部是你编写或你重构的**；课程配套源码只覆盖到「单个按键驱动 + 单任务」的量级。
**简历可以写**：独立实现三合一测量仪的应用层（万用表 / 示波器 / 信号发生器 / GUI / 任务框架），并重构了课程示例的按键驱动为回调式复用。
**唯一必须说明**：`lcd.a`（含授权校验）与 `FreeRTOS` 内核、HAL 库是第三方/课程提供，非你编写。

#### （保留）代码取证阶段的发现 —— 仍可作为佐证

> 这些是在拿到课程源码**之前**、仅凭代码本身得出的结论。复核后全部**成立且与 diff 结论一致**，保留作为旁证。

| # | 发现 | 依据 | 说明 |
| --- | --- | --- | --- |
| F1 | **文件头日期不可信** | `stat` 的 birth 时间与头部声明不符 | `buzzer_task.c` 头部写 `Mar 21, 2026`，实际创建 `2026-05-01`；`dmm.c` 头部 `Apr 5` 实际 `May 10`。说明流程是「复制模板 → 改头部日期」 |

| # | 发现 | 依据 | 说明 |
| --- | --- | --- | --- |
| F1 | **文件头日期不可信** | `stat` 的 birth 时间与头部声明不符 | `buzzer_task.c` 头部写 `Mar 21, 2026`，实际创建 `2026-05-01`；`dmm.c` 头部 `Apr 5` 实际 `May 10`。说明流程是「复制模板 → 改头部日期」 |
| F2 | **存在手打拼写错误** | `buzzer_task.c` L17 注释 | `xSemaphoreCreateBianry()` —— `Binary` 拼错、`Semaphore` 也拼错。**参考实现不会有这种错** |
| F3 | **建了校准变量却不一致使用** | `dmm.c` L58 vs L69、`waveform_capture.c` L106、`waveform_generator.c` L90/L100 | L58 算出 `fVdda`（VREFINT 反推）用于 L60/L63，但 L69 触发电压和另外 3 处仍硬编码 `3.3f` |
| F4 | **注释掉的"学步"痕迹** | `buzzer_task.c` L27-30、`lcd_task.c` L168 | 被注释的 `HAL_GPIO_WritePin` + `vTaskDelay` 闪烁序列、被注释的阻塞式 `HAL_SPI_Transmit`（后改 DMA） |
| F5 | **六个按键文件高度同构** | `Tasks/Keys/*.c` | 回调体都是「`Buzzer_Beep()` + 4 个面板操作」，仅目标面板与 `±1` 不同 → 复制模板填空 |
| F6 | **源码树里混入 Windows 二进制** | `App/Drivers/` | `lcd_tool.exe`（PE32 console 程序）、`lcd.a`（ar 归档）→ 开发机是 Windows |
| F7 | **统一 LF 行尾** | 全 `App/` 层 | 源于 Windows 却全 LF → 曾经过统一格式化（可能由 CubeIDE/工具链处理） |

#### （已废弃）旧逐模块归属表 —— 保留仅为对照，结论以上方 diff 为准

> ⚠️ 下表是**仅凭代码取证**得出的判定，其中「按键驱动 = 跟课手打」「最可能照抄」**已被课程原码 diff 证伪**。
> 保留在此是为了让后来人能看出"只看代码"会得出什么错误结论 —— **不要引用下表**。

#### ⚠️ 另需注意：`lcd.a` 内含授权校验代码

`lcd.a` 的符号表里有 `licio.c`、`rsa.c`、`bn_mod_mul.c`、`xor_encrypt.c` —— 即**授权（license）校验 + RSA 非对称加密**。这说明该预编译库带授权保护机制。

**对你的影响**：若屏幕出现花屏/不显示，**先怀疑这个库的授权校验**（可能绑定特定芯片/授权文件），而不一定是你的 SPI/DMA 配置问题。排查顺序建议：先确认同板同工程能否正常显示 → 再查 SPI/DMA → 最后怀疑库授权。
这一点也写进了 `docs/06` 的排查方向表。

## `course-reference`（✅ 已归档 —— 在**独立私有仓库**）

课程配套源码已从 bench 完整拷出并归档，但**不在本公开仓库**：

> 🔗 **[`https://github.com/finnyoun9/stm32-freertos-course-reference`](https://github.com/finnyoun9/stm32-freertos-course-reference)** （私有）

**为什么拆开**：课程配套源码与课程 PDF 版权归课程作者，**不含再分发权**，不适合放在公开仓。
但它正是上表「归属结论」做 diff 的**对照组**，必须留存以便日后复核 —— 所以放进一个独立私有仓。

| 项 | 值 |
| --- | --- |
| 内容 | 19 个 example（仅免费章节）+ `_course-docs/`（课程 PDF） |
| 规模 | 771 文件 / 约 23 MB |
| 已剔除 | `Drivers/CMSIS`、`Drivers/STM32F1xx_HAL_Driver`（厂商库 ~79 MB）、编译产物 |
| 本公开仓 | 已 `.gitignore` 排除 `firmware/course-reference/` |

**成本对比**：用了独立私有仓后，本公开仓干净无版权风险，而课程资料也已上云 ——
**以后复核归属不需要再登录 bench**。

### 原始来源（保留备查）

| 项 | 值 |
| --- | --- |
| bench 原始路径 | `D:\BaiduNetdiskDownload\FreeRTOS课程资料\配套源码持续更新~` |
| 解压产物（临时） | `D:\_rtmp`（可删） |
| 未拷入 | `教材草稿 20260603.one`（420 MB）、`1.2 部署开发环境/`（1.4 GB IDE 安装包） |

## 归档要求

| 项 | 要求 |
| --- | --- |
| 编译产物 | **不提交**（`Debug/` `Objects/` `Listings/` `*.elf` `*.map` `*.o` 等，已在 `.gitignore`） |
| CubeMX 配置 | 必须保留 `.ioc`（时钟与外设的唯一事实源） |
| FreeRTOS 内核 | 保留实际使用的版本与 `FreeRTOSConfig.h` |
| 大文件 | 课程资料不要整包塞进来，只放实际用到的部分 |
| 与文档的对应 | `docs/03` 里「我的实现」列写的文件名，必须能在这一层找到 |
