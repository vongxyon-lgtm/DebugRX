# DebugRx

**中文** · [English](#english)

一个开源的 Claude 技能（Skill）：让大模型**实际操作**一个正在运行的手机 App / 小程序 / Mini App / H5，按标准流程逐页测试，找出 bug 和可见的安全问题，并交出带复现步骤的报告。它是黑盒手测，不是代码审查。

面向：已发布或测试中的 Telegram Mini App、微信/支付宝小程序、iOS 模拟器里的 App、Android 模拟器或真机、移动端 Web。

## 它解决什么问题

让模型"找 bug"时，常见结果是读一遍源码、列一堆猜测。DebugRx 把流程固定下来：先确认测的是屏幕上的哪个 app，拿到控制权，画出页面地图，再按 9 类探测逐页测，候选问题必须从干净状态复现两次才算确认，最后还原状态、释放控制，按固定结构写报告。流程里还包含一次真实测试（Babobuy）的完整记录，包括走错的地方。

## 需要准备什么

1. 目标 app 已经在运行：Telegram 桌面版里打开的 Mini App、开发者工具里的小程序、已启动的 iOS/Android 模拟器、或一个 URL。
2. 对应的控制通道：
   - Telegram / 小程序开发者工具 → Claude 桌面应用的"电脑控制"，并在弹窗里授权该应用
   - iOS 模拟器 → Claude Code 的 iOS Simulator 工具或 `xcrun simctl`
   - Android → `adb`
   - H5 → 内置浏览器或 Claude in Chrome
3. 说清楚**哪些操作不能做**：建房间/下单/发帖、邀请、分享、付款、删号、授权权限。技能默认在这些地方停下来问你。
4. 说明是生产环境还是测试包。

## 怎么做（六个阶段）

| 阶段 | 做什么 | 结束标志 |
|---|---|---|
| 0 准备 | 确认目标 app（屏幕上的，不是某个 zip）、选平台指南、约定禁区、开一个记录文件 | 记录文件顶部写好这四项 |
| 1 连接 | 按平台指南拿到控制权；认清会把你"弹出去"的系统控件（Back/Close、Home 手势）；知道怎么重开 | 一张 app 自身界面的截图，能说出所有一级导航 |
| 2 建图 | 每个 tab 和入口过一遍，不深测；记"显示什么 / 链到哪 / 是否写数据" | 一张页面地图 |
| 3 探索 | 逐页按 9 类探测：返回栈、跨页一致性、多语言、输入校验、图表、状态持久化、加载/空/错误态、权限与设备、安全观察 | 候选问题清单 |
| 4 复现 | 每个候选从干净状态重做，**两次**才算确认；此时就写复现步骤并定严重度 | 确认清单 |
| 5 还原 | 切回设置、清掉或记录测试数据、释放所有控制 | app 回到初始页 |
| 6 报告 | 确认 bug/安全问题 → 只出现一次的 → 小问题 → 验证正常 → 本次副作用 → 未测项 | 用用户的语言写完 |

**从哪开始**：拿到 app 自身界面的截图并能说出一级导航。**到哪结束**：app 回到初始状态（或每个遗留都写明）、控制全部释放、报告写完。

## 目录

```
DebugRx/
├── SKILL.md                                  # 主流程（模型触发后读取）
├── README.md
├── LICENSE                                   # MIT
├── references/
│   ├── checklist.md                          # 9 类探测清单，附真实例子
│   ├── security-observations.md              # 黑盒、非侵入的安全观察项
│   ├── report-template.md                    # 报告模板与排序规则
│   ├── platforms/
│   │   ├── telegram-miniapp.md               # Telegram 桌面版：窗口、锁、Back/Close 陷阱、误关恢复
│   │   ├── wechat-miniprogram.md             # 微信/支付宝开发者工具
│   │   ├── ios-simulator.md
│   │   ├── android.md                        # adb，模拟器或真机
│   │   └── mobile-web.md                     # H5/PWA，浏览器工具
│   └── case-studies/
│       └── babobuy-telegram-miniapp.md       # 一次完整测试：6 个 bug 怎么被发现，两次失误怎么处理
└── evals/
    └── finds-bugs-in-running-app/            # 测试用例（claude plugin eval 可读）
```

## 安装

- Claude Code：把 `DebugRx/` 放进 `~/.claude/skills/`，或作为插件的 `skills/DebugRx/`。
- Claude 桌面应用 / claude.ai：导入打包好的 `DebugRx.skill`。

打包：在 skill-creator 目录下 `python -m scripts.package_skill path/to/DebugRx`。

## 贡献

欢迎补充平台指南（鸿蒙、iOS 真机镜像、Flutter 桌面）、更多案例、更多探测项。规则：`SKILL.md` 不超过 300 行，细节放 `references/`；每条探测项带"错的样子"和一个真实例子；案例要写出失误和副作用，不只写战果。

---

## English

An open-source Claude skill that makes the model **actually operate** a running mobile app, mini app or mobile web app, test it screen by screen along a fixed flow, and return bugs and visible security weaknesses with reproduction steps. Black-box, hands-on; not a code review.

Targets: released or in-testing Telegram Mini Apps, WeChat/Alipay mini programs, iOS apps in the Simulator, Android apps in an emulator or on a USB device, and H5/PWA.

### What it fixes

Ask a model to "find bugs" and you often get a source read and a list of guesses. DebugRx fixes the process: confirm which app on screen is the target, obtain control, draw a page map, run nine probe categories on every screen, reproduce each candidate twice from a clean state, restore and release, then report in a fixed structure. It ships with a full write-up of one real session (Babobuy), mistakes included.

### What you need

1. The app already running: a Mini App open in Telegram Desktop, a mini program in its DevTools, a booted iOS/Android simulator, or a URL.
2. A control channel: the Claude desktop app's computer-use for Telegram/DevTools; the iOS Simulator tool or `xcrun simctl`; `adb`; the built-in browser or Claude in Chrome for web.
3. Your off-limits list: create room/order/post, invite, share, pay, delete account, grant permissions. The skill stops and asks at those points by default.
4. Whether it is production or a test build.

### The flow

| Phase | Do | Done when |
|---|---|---|
| 0 Prepare | Confirm the target (on screen, not a zip), pick the platform guide, agree what is off-limits, open a log | Four lines at the top of the log |
| 1 Connect | Obtain control per the platform guide; identify the host controls that eject you; know the recovery route | A screenshot of the app's own UI; you can name its top-level navigation |
| 2 Map | One pass over every entry: shows / links to / writes data | A page map |
| 3 Explore | Per screen, nine categories: navigation stack, cross-screen consistency, localisation, input validation, data & charts, state & persistence, loading/empty/error, permissions & device, security observations | A candidate list |
| 4 Reproduce | Each candidate from a clean state, twice; write steps and severity now | A confirmed list |
| 5 Restore | Settings back, test data removed or named, every control released | App on its root screen |
| 6 Report | Confirmed → observed once → minor → verified OK → side effects → not tested | Written in the user's language |

**Starts** when you hold a screenshot of the app's own UI. **Ends** when the app is back as found (or every leftover is named), controls are released, and the report is written.

### Install

Claude Code: put `DebugRx/` in `~/.claude/skills/` or under a plugin's `skills/`. Claude desktop / claude.ai: import the packaged `DebugRx.skill`.

### Contributing

Platform guides (HarmonyOS, real-iPhone mirroring, Flutter desktop), more case studies, more probes. Rules: `SKILL.md` stays under 300 lines, details go in `references/`; every probe has a "wrong looks like" and a real example; case studies record mistakes and side effects, not just wins.

## License

MIT — see [LICENSE](LICENSE).
