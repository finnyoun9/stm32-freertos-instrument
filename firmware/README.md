# firmware · 代码归档

> 这一层放**代码**，并且严格区分来源。记录仓库的价值在于「哪段是我写的」，混在一起就说不清了。

## 目录

```text
firmware/
├── my/
│   └── demo/          # 成品工程（STM32CubeIDE），2026-09-18 从 bench 导入
├── course-reference/  # 课程各章配套源码（尚未归档，见下）
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

### 归属结论（待填）

| 模块 | 文件 | 来源（自己写 / 跟敲 / 模板改 / 课程源码） | 依据 |
| --- | --- | --- | --- |
| 任务框架 | `Core/Src/main.c` | 待填 | |
| 按键驱动 | `App/Drivers/key.c`、`App/Tasks/Keys/*` | 待填 | |
| LCD 任务 | `App/Tasks/lcd_task.c` | 待填 | |
| GUI 面板 | `App/GUI/*` | 待填 | |
| 万用表 | `App/dmm.c` | 待填 | |
| 示波器采集 | `App/waveform_capture.c` | 待填 | |
| 信号发生器 | `App/waveform_generator.c` | 待填 | |
| LCD 库 | `App/Drivers/lcd.a` + `lcd.h` | 课程提供的预编译库（确定） | 二进制 + 头文件注释 |

## `course-reference`（尚未归档）

课程资料（百度网盘 `FreeRTOS课程资料/配套源码持续更新~`）里有各章 example，但**只有免费章节**：

```
1.3 example1/2/3、2.2 example1、3.1 example2/4、3.3 example1、
3.4 example1/3、4.1 example1/2、4.2 example1、4.3 example1/2/3、4.4 example1/2、p1.1、p1.2
```

都是 `.rar`。要不要归档进 `course-reference/`，取决于「源码归属确认」的结果——**如果 demo 里有大量模板代码，把课程源码放进来反而更能说清自己写了什么**。

## 归档要求

| 项 | 要求 |
| --- | --- |
| 编译产物 | **不提交**（`Debug/` `Objects/` `Listings/` `*.elf` `*.map` `*.o` 等，已在 `.gitignore`） |
| CubeMX 配置 | 必须保留 `.ioc`（时钟与外设的唯一事实源） |
| FreeRTOS 内核 | 保留实际使用的版本与 `FreeRTOSConfig.h` |
| 大文件 | 课程资料不要整包塞进来，只放实际用到的部分 |
| 与文档的对应 | `docs/03` 里「我的实现」列写的文件名，必须能在这一层找到 |
