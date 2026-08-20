
CubeMX 是一个**图形化配置工具**：你在图上点点鼠标（选引脚、配时钟），它帮你生成一整套初始化代码，省去手写几百行寄存器配置。

1. **准备工作**：新建一个全英文路径的文件夹（如 `D:\stm32\lesson1`），作为工程根目录。
2. **打开 CubeMX**：`File → New Project`，进入 MCU 选择界面（旧版叫 Access to MCU Selector，位置不同但功能一样）。
3. **选芯片**：在 Part Number 搜索框输入芯片型号（战队工程以 STM32H723VGTx 为例，达妙 DM_MC02 开发板；**实际型号看板子丝印/战队要求，封装后缀也要对**）→ 双击选中 → Start Project。
   - 自查点 ✔：芯片图上方显示你选的完整型号。
4. **配引脚**（Pinout & Configuration 页）：点开右侧芯片图，点击 `PA5` → 弹出菜单选 `GPIO_Output`；点击 `PA0` → 选 `GPIO_Input`。然后在 `System Core → GPIO` 里分别给它们起标签（User Label）：`LED`、`KEY`，并把 KEY 的上拉设为 `Pull-up`。
   - 自查点 ✔：芯片图上 PA5、PA0 变成绿色；左侧 GPIO 列表出现 LED、KEY。
5. **配时钟**（Clock Configuration 页）：输入板子实际晶振频率（HSE，**看原理图**，战队 DM_MC02 板为 24 MHz）→ 配置 PLL 让 SYSCLK 达到 480 MHz（H723 上限 550 MHz，战队工程配置为 480 MHz）。不会算就点自动求解按钮（旧版叫 "Resolve Clock Issues"）。
   - 自查点 ✔：图中 SYSCLK 显示 480 MHz，没有红色报错。
6. **生成工程**（Project Manager 页）：工程名用字母/数字/下划线，路径选刚建的全英文文件夹；Toolchain / IDE 选 `MDK-ARM V5` → 点右上角 `GENERATE CODE`。
   - 自查点 ✔：工程文件夹里出现 `MDK-ARM/xxx.uvprojx`。
7. **打开工程**：双击 `.uvprojx` 用 Keil 打开，左侧能看到 `Drivers/STM32H7xx_HAL_Driver` 和 `Core/Src/main.c`。
   - 自查点 ✔：按 `F7` 能编译通过（0 Error），说明环境链路完整。

> 补充：战队框架的 CubeMX 工程还开启了 **FreeRTOS**（Middleware → FREERTOS），上层用 RTOS 任务（如 `osDelay`）来调度，而不是只有一个 `while(1)` 主循环。本节先学会点灯/按键的裸机写法，2.3 会讲 RTOS 怎么接管。
