# 架构图（Archify 生成）

本目录的图由 [Archify](https://github.com/tt-a1i/archify) 从同目录的 JSON 规格生成，是**自包含 HTML**（内联 SVG，含明暗主题 / 平移缩放 / 搜索 / 演示 / PNG·SVG·WebM 导出）。

图的依据全部来自 `firmware/my/demo` 的实际代码（「代码事实」口径），**没实测的结论不画进图**——实测缺口写在卡片里，也列在 `docs/08-待补与下一步.md`。

## 图索引

| # | 图 | 类型 | 回答什么问题 | 证据锚点 |
| --- | --- | --- | --- | --- |
| 1 | [`freertos-instrument-core.html`](freertos-instrument-core.html) | architecture（架构） | 三合一仪器（示波器 / 万用表 / 信号发生器）共用的一套 ADC·DMA·LCD·按键框架长什么样；五个任务怎么分优先级；IPC 谁给谁 | **任务**：`Core/Src/main.c:134-137`（vKeyTask prio3 / vBuzzerTask prio1 / vLCDTask prio1 / vLEDTask prio0）、`docs/05-成品功能与实现.md` §3（栈与唤醒源）；**IPC**：`App/dmm.c:25,78`（邮箱 `xQueueCreate(1,…)`，ISR `xQueueOverwriteFromISR`）、`App/Tasks/lcd_task.c:37,42,58,66`（事件组 9 位、SPI DMA 二值信号量）、`App/Tasks/buzzer_task.c:18`（计数信号量 5,0）；**触发链**：`App/waveform_capture.c:32,35,89,92,110`（Hold-Off 10 ms 单次 / Force 100 ms 周期 / ISR 里启动与复位）、`Core/Src/main.c:642`（EXTI3 优先级）、`App/dmm.c:69`（注入序列 rank4 读触发电压）；**按键→面板**：`App/Tasks/key_task.c`、`App/Tasks/Keys/key1.c`（回调直接调 `vRunModePanelSelect()` 等）、`App/GUI/generator_panel.c:174,197`（面板写 DAC 参数） |

## 图上标注的已知隐患（都在代码里核过）

| 项 | 位置 | 说明 |
| --- | --- | --- |
| DAC 的 DMA 中断优先级 0 | `Core/Src/main.c:556`（`HAL_NVIC_SetPriority(DMA2_Channel3_IRQn, 0, 0)`） | `configMAX_SYSCALL_INTERRUPT_PRIORITY = 5<<4`（`Core/Inc/FreeRTOSConfig.h:319`）。优先级 0 比 5 更紧急，一旦该回调调用任何 FreeRTOS API 就可能间歇性崩；同文件 EXTI3=5、ADC DMA=6 都合规，只有这条例外 |
| 蜂鸣器输出被注释 | `App/Tasks/buzzer_task.c:17` 起 | 功能清单写了「音效」但实际不响，所以图里**没有**画按键→蜂鸣器链路，只在卡片说明 |
| 三角波只有上升段 | `App/waveform_generator.c` | 疑似 bug（看起来会像锯齿），待上板确认 |
| 观测宏全关 | `Core/Inc/FreeRTOSConfig.h` | `configCHECK_FOR_STACK_OVERFLOW 0`、`configGENERATE_RUN_TIME_STATS 0`，另有 `INCLUDE_uxTaskGetStackHighWaterMark 0`、`configUSE_TRACE_FACILITY 0` → 栈水位/堆余量/CPU 占用目前**查不了**；`configTOTAL_HEAP_SIZE` 只有 8192（同文件 :283），而四个任务栈合计 2.5 KB |

## 交付凭据

| 图 | 规格 SHA-256 | HTML SHA-256 | 规格大小 | HTML 大小 |
| --- | --- | --- | --- | --- |
| 1 核心运行时 | `a96ca01d4ea2431a5cf7c743f47388786e86c194fc4c093f19822bccbc285870` | `6a6c7ee56121308718680e0c6d188dcc7ebc5566b081e27591f3035298827a88` | 6,930 B | 812,568 B |

当前状态：`validate --quality showcase` → **9/9 artifact checks 通过，composition `pass`，0 error / 0 warning**；`visual-check` → 1440×900 / 1600×1000 / 1920×1080 / 2048×1320 四个视口 containment + readability 全过。

`freertos-instrument-core.visual-check.{json,html}` 与 `*.visual-check.*.png` 是浏览器证据旁证（含明暗两套截图）。**视觉复核只做到截图层面**；交互 viewer 没有逐项点过。

## 约定

- **规格 JSON 是唯一真源**：改图改 `.json`，再 `deliver` 出新 HTML。交付后的 HTML 不原地改（`deliver` 会冻结规格字节，改 HTML 凭据即失效）。
- 图里每个数值都有来源（文件名 + 行号）。代码改了图就会过时，**以代码为准**并重新生成。

## 怎么重新生成 / 校验

```bash
cd ~/.agents/skills/archify

node bin/archify.mjs validate architecture \
  /Users/finn/Projects/stm32-freertos-instrument/docs/diagrams/freertos-instrument-core.architecture.json \
  --quality showcase --json

node bin/archify.mjs deliver architecture \
  /Users/finn/Projects/stm32-freertos-instrument/docs/diagrams/freertos-instrument-core.architecture.json \
  /Users/finn/Projects/stm32-freertos-instrument/docs/diagrams/freertos-instrument-core.html \
  --quality showcase --json

# 浏览器证据（需要本机 Chrome）
node bin/archify.mjs visual-check \
  /Users/finn/Projects/stm32-freertos-instrument/docs/diagrams/freertos-instrument-core.html --json
```

## 两条版面经验（下次画图省一轮）

1. **画布宽高比要 ≥ 1.72**：viewer 只在 `viewBox 宽高比 ≥ 1.55` 时启用「按竖向预算自适应阅读宽度」，而阅读宽下限 960px；比例不足会被夹住并竖向溢出。校验器又按 930px 可用宽算字号，故 viewBox 宽度上限约 1085。本图用 1080×540。
2. **端口是稀缺资源**：节点只有四个侧面端口。本图里 `事件组` 有 4 条边（上/下/左/右全占满）、`vKeyTask` 有 3 出 1 入，所以 ADC 注入的那条边是绕右侧 x≈1045 的长走线——不是随手画的。

## 状态

本目录的图与规格均为**新增未提交文件**（仓库其余内容未改动）。下一步优先级见 `docs/08-待补与下一步.md`，与图卡片里的「最值得讲 + 已知隐患」一致。
