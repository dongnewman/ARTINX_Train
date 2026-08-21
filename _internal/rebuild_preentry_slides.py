from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "入队前培训"
TEMPLATE = (ROOT / "_internal" / "SLIDE_TEMPLATE.html").read_text(encoding="utf-8")


EXTRA_CSS = """
/* 2026-08-21 培训演示重制：离线图片与更清晰的教学排版 */
.media-split{display:grid;grid-template-columns:1.08fr .92fr;gap:20px;flex:1;min-height:0;align-items:center}
.media-split img{width:100%;max-height:310px;object-fit:contain;border-radius:14px;background:#F7F4FE;border:1px solid var(--line);padding:10px}
.source-note{font-size:10.5px;color:var(--muted);margin-top:5px;text-align:right}
.gear-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;align-items:stretch}
.gear-card{border:1px solid var(--line);border-radius:14px;padding:14px;text-align:center;background:#fff}
.gear-card .lamp{width:34px;height:34px;border-radius:50%;margin:8px auto;border:3px solid #E8E4F4;box-shadow:0 0 18px rgba(120,76,246,.18)}
.gear-card .rpm{font-size:24px;font-weight:800;color:var(--purple)}
"""


def replace_slide(html: str, title: str, new_section: str) -> str:
    pattern = re.compile(
        r'<section class="slide"[^>]*>(?:(?!<section class="slide").)*?'
        + re.escape(title)
        + r'(?:(?!<section class="slide").)*?</section>',
        re.S,
    )
    result, count = pattern.subn(new_section.strip(), html, count=1)
    if count == 0:
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", new_section, re.S)
        expected = re.sub(r"<[^>]+>", "", heading.group(1)).strip() if heading else ""
        if expected and expected in html:
            return html
    if count != 1:
        raise RuntimeError(f"未唯一找到幻灯片：{title}，匹配数 {count}")
    return result


def remove_recap_and_normalize(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = re.sub(
        r'\s*<!--[^>]*最后一页[^>]*-->\s*<section class="slide"[^>]*>.*?本节回顾.*?</section>',
        "",
        html,
        flags=re.S,
    )
    html = re.sub(
        r'\s*<section class="slide"[^>]*>(?:(?!<section class="slide").)*?本节回顾(?:(?!<section class="slide").)*?</section>',
        "",
        html,
        flags=re.S,
    )
    html = html.replace("延伸资源（均已验证可访问）", "补充内容与延伸资源")
    html = html.replace("延伸资源（课后自学）", "补充内容与延伸资源")
    html = html.replace("延伸资源（自学用）", "补充内容与延伸资源")
    html = html.replace("延伸资源（链接均已验证可访问）", "补充内容与延伸资源")
    html = html.replace(">延伸资源<", ">补充内容与延伸资源<")
    if '<link rel="icon" href="data:,">' not in html:
        html = html.replace("</head>", '<link rel="icon" href="data:,">\n</head>', 1)
    if EXTRA_CSS.strip() not in html:
        html = html.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    path.write_text(html, encoding="utf-8", newline="\n")


def update_existing_decks() -> None:
    for section in sorted(PRE.iterdir()):
        if section.is_dir() and section.name.startswith(("1.1", "1.2", "1.3", "1.4", "1.5", "1.6")):
            remove_recap_and_normalize(section / "演示文档.html")

    p13 = PRE / "1.3 单片机初步认识" / "演示文档.html"
    html = p13.read_text(encoding="utf-8")
    html = replace_slide(
        html,
        "什么是单片机",
        """
  <section class="slide">
    <h2 class="anim">C 板就是一台微型专用计算机</h2>
    <div class="media-split">
      <div>
        <p class="anim" style="animation-delay:.1s">单片机（MCU，Microcontroller Unit）把 <em>CPU、Flash、RAM 和外设</em>集成到一颗芯片。它不运行桌面软件，只按固定周期、固定优先级执行机器人控制任务。</p>
        <ul class="anim" style="animation-delay:.2s">
          <li>CPU 执行指令；Flash 保存程序；RAM 保存运行变量。</li>
          <li>GPIO、Timer、CAN、UART 等外设直接连接真实硬件。</li>
          <li>RoboMaster C 板主控为 STM32F407IGHx，板载 CAN、IMU、用户按键和 RGB LED。</li>
        </ul>
        <div class="callout tip anim" style="animation-delay:.3s;margin-top:10px">一句话：单片机是把程序变成电平、数据帧和电机动作的桥梁。</div>
      </div>
      <div class="anim" style="animation-delay:.2s">
        <img src="../../assets/training/cboard_type_c_official.jpg" alt="RoboMaster 开发板 C 型">
        <div class="source-note">图片：RoboMaster 开发板 C 型官方产品页</div>
      </div>
    </div>
  </section>
""",
    )
    html = replace_slide(
        html,
        "按键防抖：按一次只认一次",
        """
  <section class="slide">
    <h2 class="anim">按键防抖：先确认稳定，再产生一次事件</h2>
    <div class="cols">
      <div>
        <p class="anim">机械触点会在几毫秒内反复通断。主循环如果直接把“电平为低”当成一次按键，就会在按住期间连续触发。</p>
        <pre class="anim" style="animation-delay:.15s"><span class="c">/* 伪代码：非阻塞消抖 */</span>
raw = <span class="f">ReadKey</span>();
<span class="k">if</span> (raw != candidate) { candidate = raw; changed_at = now; }
<span class="k">if</span> (now - changed_at &gt;= <span class="n">20</span> &amp;&amp; stable != candidate) {
    stable = candidate;
    <span class="k">if</span> (stable == PRESSED) key_event = <span class="n">1</span>;
}</pre>
      </div>
      <div>
        <div class="card anim" style="animation-delay:.2s">
          <h3>C 板实物对应</h3>
          <table><tr><th>功能</th><th>引脚</th><th>有效电平</th></tr>
          <tr><td>用户按键</td><td>PA0</td><td>按下为低</td></tr>
          <tr><td>蓝/绿/红 LED</td><td>PH10/11/12</td><td>高电平点亮</td></tr></table>
        </div>
        <div class="callout warn anim" style="animation-delay:.3s;margin-top:10px">防抖不能用 20 ms 阻塞延时卡住 1 ms 电机控制任务；按键逻辑应产生“事件”，控制任务读取事件。</div>
      </div>
    </div>
  </section>
""",
    )
    p13.write_text(html, encoding="utf-8", newline="\n")

    p15 = PRE / "1.5 PID与闭环控制" / "演示文档.html"
    html = p15.read_text(encoding="utf-8")
    resource_marker = re.search(
        r'<section class="slide"[^>]*>(?:(?!<section class="slide").)*?补充内容与延伸资源', html, re.S
    )
    if not resource_marker:
        raise RuntimeError("1.5 未找到补充内容页")
    insert_at = resource_marker.start()
    rtt_slide = """
  <section class="slide">
    <h2 class="anim">RTT：把 PID 调参变成可复现的实验</h2>
    <div class="grid grid-3" style="flex:1;align-content:center">
      <div class="card anim"><h3>上传</h3><p>固定键名输出 Target、Speed、Error、Output 和参数；控制环 1 kHz，RTT 可降到 200 Hz。</p></div>
      <div class="card anim" style="animation-delay:.1s"><h3>观察</h3><p>目标与反馈同图，检查上升时间、超调、稳态误差、调节时间和输出饱和。</p></div>
      <div class="card green anim" style="animation-delay:.2s"><h3>迭代</h3><p>一次只改一个参数，保存 CSV 与失败参数；曲线证据决定下一步，不凭“听起来顺”。</p></div>
    </div>
    <pre class="anim" style="animation-delay:.3s">Time:1250,Target:3000,Speed:2875,Error:125,Output:4120,Kp:0.80,Ki:0.02,Kd:0.00</pre>
    <div class="callout tip anim" style="animation-delay:.4s;margin-top:10px">下一节大作业会要求用战队 RTT 工具保存三轮数据，并在线调整 PID 参数。</div>
  </section>

"""
    if "RTT：把 PID 调参变成可复现的实验" not in html:
        html = html[:insert_at] + rtt_slide + html[insert_at:]
    html = re.sub(r"[ \t]+$", "", html, flags=re.M)
    p15.write_text(html, encoding="utf-8", newline="\n")


def s(title: str, body: str, theme: str = "") -> str:
    attr = ' data-theme="purple"' if theme else ""
    return f'<section class="slide"{attr}>\n{body}\n</section>'


def build_assignment_deck() -> None:
    prefix, tail = TEMPLATE.split('<div id="deck">', 1)
    _, suffix = tail.split("</main>", 1)
    framework = suffix.split("/* ================= 交互演示注册区（各小节自行编写） ================= */", 1)[0]
    slides: list[str] = []
    slides.append(s("封面", """
    <img class="cover-logo anim" src="../../assets/ARTINX.png" alt="ARTINX">
    <div class="cover-center"><div class="sec anim">1.7　入队综合作业</div>
      <h1 class="anim" style="animation-delay:.15s">四档电机速度控制器</h1>
      <div class="cover-divider anim" style="animation-delay:.25s"></div>
      <div class="sub anim" style="animation-delay:.35s">C 板按键 · RGB LED · PID 速度环 · RTT 数据调参</div>
    </div><div class="cover-sign anim" style="animation-delay:.45s">电控组长 董心宇</div>
""", "purple"))
    slides.append(s("完成线", """
    <h2 class="anim">完成线不是“电机转了”，而是闭环、可测、可解释</h2>
    <div class="gear-row" style="margin-top:18px">
      <div class="gear-card anim"><h3>0 档</h3><div class="lamp"></div><div class="rpm">0</div><p>上电默认，输出清零</p></div>
      <div class="gear-card anim" style="animation-delay:.1s"><h3>低速</h3><div class="lamp" style="background:#3B82F6"></div><div class="rpm">1000</div><p>蓝灯，方向与基线</p></div>
      <div class="gear-card anim" style="animation-delay:.2s"><h3>中速</h3><div class="lamp" style="background:#22C55E"></div><div class="rpm">3000</div><p>绿灯，主要调参</p></div>
      <div class="gear-card anim" style="animation-delay:.3s"><h3>高速</h3><div class="lamp" style="background:#EF4444"></div><div class="rpm">5000</div><p>红灯，最后验证</p></div>
    </div>
    <div class="callout tip anim" style="margin-top:16px;animation-delay:.4s">每按一次 KEY：0 → 低 → 中 → 高 → 0；三档都必须由 PID 根据 CAN 反馈闭环控制。</div>
"""))
    slides.append(s("硬件与安全", """
    <h2 class="anim">先把危险路径关掉，再开始写控制</h2>
    <div class="media-split"><div>
      <ul class="anim"><li>C 板、统一 CAN 电机与电调、调试器、限流电源、固定台架。</li>
      <li>输出轴周围无松散线缆；不得手持高速电机或用手增加负载。</li>
      <li>第一次上电保持 0 档；第一次闭环从低速和小输出限幅开始。</li>
      <li>异响、反向加速、过热、CAN 掉线：立即断电。</li></ul>
      <div class="callout danger anim" style="animation-delay:.2s;margin-top:12px">上电高速转、掉线继续输出、无输出限幅，均为验收红线。</div>
    </div><div class="anim"><img src="../../assets/training/cboard_type_c_official.jpg" alt="RoboMaster 开发板 C 型"><div class="source-note">图片：RoboMaster 官方产品页</div></div></div>
"""))
    slides.append(s("引脚", """
    <h2 class="anim">C 板引脚按官方手册配置，不凭经验猜</h2>
    <table class="anim"><tr><th>功能</th><th>引脚</th><th>有效电平</th><th>作业用途</th></tr>
      <tr><td>KEY</td><td>PA0</td><td>按下为低</td><td>产生一次档位切换事件</td></tr>
      <tr><td>LED_B</td><td>PH10</td><td>高电平点亮</td><td>低速档</td></tr>
      <tr><td>LED_G</td><td>PH11</td><td>高电平点亮</td><td>中速档</td></tr>
      <tr><td>LED_R</td><td>PH12</td><td>高电平点亮</td><td>高速档；故障时闪烁</td></tr></table>
    <div class="grid grid-2" style="margin-top:14px"><div class="card anim"><h3>CubeMX</h3><p>起始 `.ioc` 可能未启用这些 GPIO。配置后重新生成，并检查自定义代码仍在 USER CODE 区域。</p></div><div class="card green anim"><h3>单色自测</h3><p>电机不通电，逐个点亮蓝/绿/红，再读 PA0 原始值；先证明引脚，再写状态机。</p></div></div>
"""))
    slides.append(s("模式", """
    <h2 class="anim">模式管理只接受“按下事件”，不直接跟随原始电平</h2>
    <div class="demo-stage anim"><canvas data-demo="modecycle"></canvas><div class="demo-controls"><button class="btn" id="modeNext">模拟按下一次 KEY</button><button class="btn ghost" id="modeReset">上电复位</button><span class="small muted" id="modeText">当前：0 档</span></div></div>
"""))
    slides.append(s("防抖", """
    <h2 class="anim">非阻塞防抖：稳定 20 ms 后只发一次事件</h2>
    <div class="cols"><div><pre class="anim">raw = ReadKey();
if (raw != candidate) {
    candidate = raw;
    changed_at = now;
}
if (now - changed_at &gt;= 20 &amp;&amp; stable != candidate) {
    stable = candidate;
    if (stable == PRESSED) key_event = 1;
}</pre></div><div><ul class="anim"><li>按住期间 stable 不再变化，所以不会连跳。</li><li>机械弹跳只会更新 candidate，不立即改变档位。</li><li>不得用 20 ms `HAL_Delay()` 阻塞 1 ms 控制任务。</li><li>验收会连续按 8 次并故意长按。</li></ul></div></div>
"""))
    slides.append(s("模块", """
    <h2 class="anim">四个职责分开，调试时才能逐层定位</h2>
    <div class="grid grid-4" style="flex:1;align-content:center"><div class="card anim"><h3>Button</h3><p>读 PA0、消抖、产生一次事件</p></div><div class="card anim" style="animation-delay:.1s"><h3>ModeManager</h3><p>四档状态、目标 RPM、LED 映射</p></div><div class="card anim" style="animation-delay:.2s"><h3>MotorCtrl</h3><p>CAN 反馈、PID、限幅、发送控制量</p></div><div class="card green anim" style="animation-delay:.3s"><h3>Telemetry</h3><p>RTT 上传、参数写入、CSV 证据</p></div></div>
    <div class="callout anim">名字可以不同，但不能把按键、PID、RTT 和故障逻辑堆进一个无限循环。</div>
"""))
    slides.append(s("闭环", """
    <h2 class="anim">速度环每 1 ms 更新，RTT 每 5 ms 采样</h2>
    <pre class="anim" style="font-size:15px;line-height:1.8">档位 ──▶ target_rpm ─┐
                      ├─▶ error ─▶ PID ─▶ current_cmd ─▶ CAN 电调 ─▶ 电机
CAN 反馈 ─▶ speed_rpm ┘                                          │
      ▲                                                           │
      └──────────────────── 编码器反馈 ────────────────────────────┘</pre>
    <div class="grid grid-3" style="margin-top:12px"><div class="card anim"><h3>控制任务</h3><p>固定周期，误差方向 target - feedback。</p></div><div class="card anim"><h3>停止路径</h3><p>0 档与故障：目标、输出、积分全部清零。</p></div><div class="card green anim"><h3>采样任务</h3><p>降低输出频率，避免 RTT 打印干扰控制。</p></div></div>
"""))
    slides.append(s("PID要求", """
    <h2 class="anim">PID 的“能用”包含限幅、复位和参数边界</h2>
    <table class="anim"><tr><th>要求</th><th>为什么</th><th>验收方法</th></tr><tr><td>输出限幅</td><td>限制最大电流命令</td><td>检查 Output 不越界</td></tr><tr><td>积分限幅</td><td>避免长时间累积</td><td>目标切换时无持续大冲击</td></tr><tr><td>0 档清积分</td><td>停机后不能保存旧推力</td><td>高速回 0 再进低速</td></tr><tr><td>参数集中配置</td><td>避免多处数值互相覆盖</td><td>现场修改一个参数</td></tr><tr><td>NaN/越界拒绝</td><td>在线写内存也可能写错</td><td>输入异常值不应用</td></tr></table>
"""))
    slides.append(s("RTT上传", """
    <h2 class="anim">固定键名让曲线、CSV 和报告指向同一组数据</h2>
    <pre class="anim">SEGGER_RTT_printf(0,
  "Time:%lu,Mode:%d,Target:%.2f,Speed:%.2f,"
  "Error:%.2f,Output:%.2f,Kp:%.5f,Ki:%.5f,Kd:%.5f\\n",
  Time::GetTick(), mode, target, speed,
  target - speed, output, kp, ki, kd);</pre>
    <div class="grid grid-3" style="margin-top:12px"><div class="card anim"><h3>必须</h3><p>键值对、逗号分隔、换行结束。</p></div><div class="card anim"><h3>必须</h3><p>字段语义与固件版本一致。</p></div><div class="card green anim"><h3>建议</h3><p>5 ms 输出；如丢样，再降频或减字段。</p></div></div>
"""))
    slides.append(s("PID演示", """
    <h2 class="anim">演示：一次只改一个参数，观察目标与反馈</h2>
    <div class="demo-stage anim"><canvas data-demo="pidresponse"></canvas><div class="demo-controls"><label>Kp <input id="taskKp" type="range" min="0" max="3" step="0.05" value="0.8"><span id="taskKpV">0.80</span></label><label>Ki <input id="taskKi" type="range" min="0" max="2" step="0.02" value="0.12"><span id="taskKiV">0.12</span></label><button class="btn ghost" id="pidReset">重新阶跃</button><span class="small muted">绿虚线：目标；紫线：实际；灰线：输出</span></div></div>
"""))
    slides.append(s("在线调参", """
    <h2 class="anim">在线写入必须“校验—应用—回传确认”</h2>
    <div class="grid grid-4" style="flex:1;align-content:center"><div class="card anim"><h3>1 写入</h3><p>工具把参数写入公开的 volatile 结构体。</p></div><div class="card anim"><h3>2 校验</h3><p>检查通道、ID、有限数、限幅和允许范围。</p></div><div class="card anim"><h3>3 应用</h3><p>仅参数变化时 SetParams，并安全处理积分。</p></div><div class="card green anim"><h3>4 回传</h3><p>RTT 返回当前 Kp/Ki/Kd，确认真正生效。</p></div></div>
    <div class="callout warn anim">工具当前通过调试器直接写内存；重新编译后地址可能变化。旧 ELF/MAP 地址禁止继续使用。</div>
"""))
    slides.append(s("三轮实验", """
    <h2 class="anim">至少三轮数据，其中一轮必须“不够好”</h2>
    <table class="anim"><tr><th>轮次</th><th>目的</th><th>只允许改什么</th><th>交付证据</th></tr><tr><td>A</td><td>只有 P 的基线</td><td>先扫 Kp，Ki=Kd=0</td><td>CSV、曲线、现象</td></tr><tr><td>B</td><td>针对问题改进</td><td>只改 P 或只加入 I</td><td>与 A 同条件对比</td></tr><tr><td>C</td><td>最终三档循环</td><td>锁定最终参数</td><td>0/低/中/高/0 完整数据</td></tr></table>
    <div class="callout tip anim" style="margin-top:14px">记录前写预测，记录后写结果：每轮都要能回答“为什么这样改、数据支持什么结论”。</div>
"""))
    slides.append(s("指标", """
    <h2 class="anim">不要只看“曲线挺顺”，用五个指标说话</h2>
    <div class="grid grid-3" style="flex:1;align-content:center"><div class="card anim"><h3>上升时间</h3><p>进入目标附近用了多久。</p></div><div class="card anim"><h3>最大超调</h3><p>峰值超过目标多少。</p></div><div class="card anim"><h3>稳态误差</h3><p>稳定后平均值与目标之差。</p></div><div class="card anim"><h3>调节时间</h3><p>进入并持续保持在误差带内多久。</p></div><div class="card anim"><h3>饱和比例</h3><p>输出有多少时间顶住限幅。</p></div><div class="card green anim"><h3>数据质量</h3><p>时间单调、字段齐全、固件与日志匹配。</p></div></div>
"""))
    slides.append(s("功能验收", """
    <h2 class="anim">功能验收：8 次按键 + 断线测试</h2>
    <div class="cols"><div><ol class="anim"><li>上电 3 s 内电机不转，LED 熄灭。</li><li>连续按 8 次，四档严格循环两轮。</li><li>故意长按，不能连续跳档。</li><li>蓝/绿/红对应低/中/高。</li><li>三档均由 PID 闭环，不是固定电流。</li></ol></div><div><ol class="anim" start="6"><li>高速回 0 后输出与积分清零。</li><li>断开 CAN，100 ms 内停机并红灯闪烁。</li><li>恢复 CAN 后不得自动高速重启。</li></ol><div class="callout danger anim" style="margin-top:12px">故障必须回到 0 档或重新上电后再恢复。</div></div></div>
"""))
    slides.append(s("性能验收", """
    <h2 class="anim">性能验收：统一目标、统一台架、统一误差带</h2>
    <table class="anim"><tr><th>项目</th><th>要求</th><th>数据证据</th></tr><tr><td>稳态误差</td><td>低/中/高均在目标 ±5%</td><td>稳定区间平均值</td></tr><tr><td>调节时间</td><td>2 s 内进入并保持在 ±5%</td><td>Target/Speed 曲线</td></tr><tr><td>振荡与饱和</td><td>无持续振荡、无长时间饱和</td><td>Error/Output 曲线</td></tr><tr><td>长期运行</td><td>四档循环 5 min 无异常</td><td>完整 CSV 与现场演示</td></tr></table>
    <div class="callout anim" style="margin-top:14px">若硬件条件需要修改目标或阈值，导师必须在发题前统一修改，不能现场对个人临时放宽。</div>
"""))
    slides.append(s("提交", """
    <h2 class="anim">提交的是可复验工程，不是一段演示视频</h2>
    <pre class="anim">姓名_入队作业/
├─ source/          最终源代码与工程
├─ firmware/        可烧录固件
├─ rtt_logs/        A / B / C 三轮 CSV
├─ figures/         至少两张曲线
├─ REPORT.md        参数、指标、结论
├─ DEBUG_LOG.md     两个真实问题的证据链
└─ README.md        接线、编译、烧录、操作</pre>
    <div class="callout tip anim" style="margin-top:12px">发放框架是去 Git 版本；本作业不要求 Git 历史，也不要为了评分伪造提交记录。</div>
"""))
    slides.append(s("评分", """
    <h2 class="anim">100 分里，RTT 数据与在线调参占 35 分</h2>
    <table class="anim"><tr><th>项目</th><th>分值</th><th>关键证据</th></tr><tr><td>四档与 LED</td><td>20</td><td>防抖、顺序、颜色、上电 0 档</td></tr><tr><td>PID 速度闭环</td><td>25</td><td>固定周期、限幅、三档性能</td></tr><tr><td>RTT 监控与保存</td><td>20</td><td>字段、曲线、三轮 CSV</td></tr><tr><td>RTT 在线调参</td><td>15</td><td>写入、校验、应用、回读</td></tr><tr><td>安全与异常</td><td>10</td><td>零输出、CAN 超时、故障不自启</td></tr><tr><td>工程说明与答辩</td><td>10</td><td>可复验、能解释、能现场修改</td></tr></table>
"""))
    slides.append(s("补充", """
    <h2 class="anim">补充内容与资料：都已放在本节文件夹</h2>
    <div class="grid grid-2" style="flex:1;align-content:center"><div class="card anim"><h3>离线资料</h3><ul><li>去 Git 战队代码框架 ZIP</li><li>去 Git RTT 工具 ZIP</li><li>C 板、M3508、C620 官方手册</li><li>RTT 调参指南与评分验收表</li></ul></div><div class="card anim"><h3>在线入口</h3><ul><li><a href="https://www.robomaster.com/zh-CN/products/components/general/development-board-type-c">RoboMaster C 板产品页</a></li><li><a href="https://www.segger.com/products/debug-probes/j-link/technology/about-real-time-transfer/">SEGGER RTT 技术介绍</a></li><li><a href="https://www.st.com/en/microcontrollers-microprocessors/stm32f407-417.html">STM32F407/417 官方页</a></li></ul></div></div>
    <div class="callout warn anim">在线参数写入目前依赖当前固件内存地址；以随附指南和当前 MAP/ELF 为准。</div>
"""))
    slides.append(s("开始", """
    <img class="end-logo anim" src="../../assets/ARTINX.png" alt="ARTINX">
    <div class="cover-center"><div class="sec anim">START SAFE</div><h1 class="anim" style="font-size:38px">第一步：电机不通电，只做按键和灯</h1><div class="cover-divider anim"></div>
      <ul class="anim" style="font-size:17px;line-height:1.9"><li>核对 PA0、PH10、PH11、PH12</li><li>单色点亮蓝、绿、红</li><li>实现非阻塞防抖与四档循环</li><li>通过连续 8 次按键测试后，再接电机</li></ul></div>
""", "purple"))

    demo_js = r'''
/* ================= 交互演示注册区（1.7） ================= */
function fit(c) {
  const r = c.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  const nextW = Math.round(r.width*dpr), nextH = Math.round(r.height*dpr);
  if (c.width !== nextW || c.height !== nextH) { c.width = nextW; c.height = nextH; }
  const ctx=c.getContext('2d'); ctx.setTransform(dpr,0,0,dpr,0,0); return {w:r.width,h:r.height,ctx};
}
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
let taskMode=0;
const modeNames=['0 档','低速','中速','高速'], modeRpms=[0,1000,3000,5000], modeColors=['#E8E4F4','#3B82F6','#22C55E','#EF4444'];
ARTINX_DEMOS['modecycle']={
  init(c){ const {w,h,ctx}=fit(c); ctx.clearRect(0,0,w,h); const gap=w/4; for(let i=0;i<4;i++){const x=gap*(i+.5); ctx.beginPath();ctx.arc(x,h*.42,34,0,Math.PI*2);ctx.fillStyle=modeColors[i];ctx.fill();ctx.lineWidth=i===taskMode?7:2;ctx.strokeStyle=i===taskMode?'#784CF6':'#C9C3DE';ctx.stroke();ctx.textAlign='center';ctx.fillStyle='#262034';ctx.font='bold 17px Segoe UI';ctx.fillText(modeNames[i],x,h*.72);ctx.font='13px Segoe UI';ctx.fillStyle='#5A5468';ctx.fillText(modeRpms[i]+' RPM',x,h*.82);if(i<3){ctx.strokeStyle='#784CF6';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x+42,h*.42);ctx.lineTo(x+gap-42,h*.42);ctx.stroke();}}
    document.getElementById('modeText').textContent='当前：'+modeNames[taskMode]+' / '+modeRpms[taskMode]+' RPM'; }, destroy(){}
};
document.getElementById('modeNext').onclick=()=>{taskMode=(taskMode+1)%4;go(cur)};
document.getElementById('modeReset').onclick=()=>{taskMode=0;go(cur)};

let pidResetRequested=false;
ARTINX_DEMOS['pidresponse']=(()=>{let raf=0,last=0,acc=0,t=0,v=0,integ=0,hist=[]; const dt=.005;
  function reset(){t=0;v=0;integ=0;hist=[];}
  function step(){const kp=+document.getElementById('taskKp').value,ki=+document.getElementById('taskKi').value,target=3000,e=target-v;integ=clamp(integ+ki*e*dt,-5000,5000);const out=clamp(kp*e+integ,0,10000);v+=(out*.42-v)*dt/.32;t+=dt;hist.push({t,v,out});while(hist.length&&hist[0].t<t-8)hist.shift();}
  function draw(c){const {w,h,ctx}=fit(c);ctx.clearRect(0,0,w,h);const L=45,R=w-12,T=14,B=h-42,X=x=>L+(x-(t-8))/8*(R-L),Y=y=>B-y/5500*(B-T);ctx.strokeStyle='#E8E4F4';for(let q=0;q<=5000;q+=1000){ctx.beginPath();ctx.moveTo(L,Y(q));ctx.lineTo(R,Y(q));ctx.stroke();ctx.fillStyle='#5A5468';ctx.font='11px Segoe UI';ctx.textAlign='right';ctx.fillText(q,L-6,Y(q)+3);}ctx.setLineDash([7,5]);ctx.strokeStyle='#3C6400';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(L,Y(3000));ctx.lineTo(R,Y(3000));ctx.stroke();ctx.setLineDash([]);if(hist.length>1){ctx.beginPath();hist.forEach((p,i)=>{const x=X(p.t),y=Y(p.v);i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.strokeStyle='#784CF6';ctx.lineWidth=3;ctx.stroke();ctx.beginPath();hist.forEach((p,i)=>{const x=X(p.t),y=B-(p.out/10000)*70;i?ctx.lineTo(x,y):ctx.moveTo(x,y)});ctx.strokeStyle='#8F87AB';ctx.lineWidth=2;ctx.stroke();}ctx.fillStyle='#262034';ctx.textAlign='left';ctx.font='13px Segoe UI';ctx.fillText('Target 3000 RPM',L+8,T+16);ctx.fillText('Speed '+v.toFixed(0)+' RPM',L+8,T+34);}
  function loop(c,now){if(pidResetRequested){reset();acc=0;last=now;pidResetRequested=false;}if(last){acc=Math.min(.2,acc+(now-last)/1000);while(acc>=dt){step();acc-=dt;}}last=now;draw(c);raf=requestAnimationFrame(n=>loop(c,n));}
  return {init(c){last=0;if(!raf)raf=requestAnimationFrame(n=>loop(c,n));},destroy(){if(raf)cancelAnimationFrame(raf);raf=0;}};
})();
['taskKp','taskKi'].forEach(id=>document.getElementById(id).oninput=e=>document.getElementById(id+'V').textContent=(+e.target.value).toFixed(2));
document.getElementById('pidReset').onclick=()=>{pidResetRequested=true};
go(cur);
</script>
</body>
</html>
'''
    html = prefix.replace("</style>", EXTRA_CSS + "\n</style>", 1)
    if '<link rel="icon" href="data:,">' not in html:
        html = html.replace("</head>", '<link rel="icon" href="data:,">\n</head>', 1)
    html += '<div id="deck">\n' + "\n\n".join(slides) + "\n</div>\n</main>" + framework + demo_js
    html = html.replace("<title>1.x 节标题 · ARTINX 电控培训</title>", "<title>1.7 入队综合作业 · ARTINX 电控培训</title>")
    out = PRE / "1.7 入队综合作业" / "演示文档.html"
    out.write_text(html, encoding="utf-8", newline="\n")


def main() -> None:
    update_existing_decks()
    build_assignment_deck()
    print("已重制入队前 1.1-1.7 演示文档")


if __name__ == "__main__":
    main()
