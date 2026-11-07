# 安装 OpenMausBot，并与 ds bot 对比（含能力移植）

2026-11-07 · 执行环境：WSL (Ubuntu 24.04) on Windows 主机 · ds bot：ds-bot 0.3.1（本部署 profile 已启用）

## 1. 结论先行

- **安装**：OpenMausBot 0.1.146 已装到本机 WSL（.deb 全量安装 + 依赖修复完成），桌面
  窗口（WSLg 下以 `--disable-gpu` 启动正常）、无头 CLI、`doctor --host`、`sentinel` 自检
  全部可跑通（记录见§3）。包 269 MB，已完整安装，不存在下载未完成的问题。
- **对比**：两者的目标高度重合——"把多智能体团队做成聊天应用"。ds bot 0.3.1 已经把
  OpenMausBot 的主干能力都补齐甚至加强（IM 接入 8 个平台、群聊目标流程、记忆治理、
  office 套件、~36 个连接器）。OpenMausBot 更强的残余差异是 6 项（§4）。
- **移植**：本次把价值最高、且不改动 ds-bot 源码就能落地的 **Sentinel（健康扫描）**
  移植为 `dsbot-sentinel/`：只读扫描 ds bot 数据目录 → 按签名聚合问题 → 简报写进
  团队工作区。已安装进本部署并验证首跑（§5，首跑抓到 26 条真实问题）。
- 其余 5 项差异属于"需要改 ds-bot 插件源码 / 基础设施"级别的移植，列为建议
  （§6），未在本票内动工。

## 2. 两个项目各自是什么

| | OpenMausBot（milind-soni/OpenMausBot） | ds bot（npm `ds-bot`，本部署已跑） |
|---|---|---|
| 定位 | 开源 Grok Bot 替代：聊天窗应用里每格是常驻 Bot | DeepSeek Harness 插件：把 dsh 变成常驻 Bot 团队（主 Bot、Bot↔Bot、群聊） |
| 引擎 | 本机 claude/codex/grok CLI，可指向自定义引擎 | dsh 各模型路由；另有 10 种本地 agent 引擎（claude-code、codex、devin、open-code、cursor、gemini、grok、cline、qwen、goose + 自定义 ACP） |
| 电脑 | 云桌面(Boat)+本地 CUA 驱动+沙箱 bot-box | 直接操作宿主真实电脑（CUA），级别/租约/多 Bot 同用一个应用管控，无云 VM |
| 连接 | Composio 500+ 应用市场 | ~36 个 OAuth MCP 连接器 + 本地邮件 |
| 安装 | macOS/Win/Ubuntu 桌面应用 | dsh 插件（npm / github#ref），web + 桌面 |

## 3. 安装与验证记录（本机）

```text
$ sudo dpkg -i OpenMausBot-0.1.146-amd64.deb        # 269 MB，apt 补齐 4 个依赖
ii  openmausbot 0.1.146 amd64 Your own team of AI bots, in a chat app
$ …/resources/server/openmausbot.js doctor --host
  ok Ubuntu 24.04.5 LTS kernel 6.18.54.1-microsoft-standard-WSL2
  ok Unprivileged user namespaces are allowed / seccomp is available / cgroup v2
  FAIL 仅: 未装 Docker/Podman（云桌面/VM 功能需要，暂不需要）
  warn 磁盘未加密、2 CPU（Team 服务器规格建议）；8799 端口空闲
$ ELECTRON_RUN_AS_NODE=1 … openmausbot.js status
  WIN-CE3O4FOAUTE · OpenMausBot 0.1.146 on linux · id 33d53988-…
$ … openmausbot.js sentinel --once --json
  {"ok":true,"scanned":true,"totalIssues":0}
$ DISPLAY=:0 openmausbot --disable-gpu --no-sandbox …（WSLg 实际跑出窗口）
  xwininfo: 窗口 "MausBot" (com.openmausbot.app) 1040x760 可见
```

- WSL2 下启动桌面程序需要 `--disable-gpu`（GPU 进程在 WSLg 沙箱里打不开会 FATAL）；
  无该参数会退出，加参数即正常出窗。
- 截图（WSLg 环境下截屏内容受限，以窗口名列表+进程存活的回执为准）：
  本机 `/home/dsh/dsh-superagent/.artifacts/openmausbot/shot*.png`。
- 本机没有 claude/codex 的 Linux CLI（操作员个人的 claude/codex 在 Windows 侧）。
  OpenMausBot 的 Bot 因此**不使用任何 Claude/Codex 订阅登录**，而是接本机模型网关（见 §3.1）。

### 3.1 模型接入：让 OpenMausBot 跑在「我们的模型」上

写入 `~/.openmausbot/config.json`（模式 0600，实例在启动时读取）：

```json
{
  "instances": {
    "bob":  { "driver": "openai-compat", "displayName": "bob 家模型（agentgateway）",
              "icon": { "kind": "preset", "preset": "anthropic" },
              "config": { "url": "http://127.0.0.1:20080/v1", "model": "claude-sonnet-5",
                          "key": "local-gateway" } },
    "auto": { "driver": "openai-compat", "displayName": "Auto（本机自动路由池）",
              "config": { "url": "http://127.0.0.1:20081/v1", "model": "auto",
                          "key": "local-gateway" } }
  }
}
```

- `openai-compat` 驱动一个实例一条：`bob` 走 agentgateway（`127.0.0.1:20080/v1`，
  bob-api 等中转的模型池）；`auto` 走本机 autoroute（`127.0.0.1:20081/v1`，
  `auto`/`auto-free` 免费车道链）。两者都**无需真实密钥**（本机网关不校验），
  但该驱动的实例必须带一个 `config.key` 才判定为可用，所以填了占位串。
- 实例顺序即"新 Bot 默认模型"的优先序：`bob` 在前（稳定、快），`auto` 在后（免费）。
  已有 MausBot 的模型在 `bots.json` 的 `modelSelection` 里设为 `bob/claude-sonnet-5`。
- 桌面应用与 CLI 共读同一份配置；改完需重启应用（实例在 boot 时读取）。

验证（本轮实测）：

```text
$ openmausbot doctor              # 指向桌面应用 127.0.0.1:8799
  ready · Engines available: bob, auto
$ openmausbot engine list
  bob · bob 家模型（agentgateway） · available
  auto · Auto（本机自动路由池） · available
$ openmausbot models
  bob · available · default claude-sonnet-5 · 104 models
  auto · available · default auto · 2 models

# 真实轮次（无头服务器 + 同一配置，真实模型调用）：
$ openmausbot run 试验员 "连通性测试…" --model auto/auto
  Done · 回复："连通性正常…复述：'测试一'"          # auto 车道
$ openmausbot set-model 试验员 --model bob/claude-sonnet-5 && openmausbot run 试验员 "…"
  Done · 回复："我是Claude Sonnet 5，当前请求使用的模型。"   # bob 车道
# 桌面应用自身也已在 openai-compat 上成功完成轮次（events/*.ndjson turn.completed ok:true）
```

- `auto` 的代价：autoroute.py 是单线程顺序 fallback，一条请求实测可达 ~48s，
  并发时会互相阻塞（本机其它服务也在打它）。日常聊天可用，批量/并发任务建议用 `bob`。
- `bob` 走付费中转（metered），按 token 计费；`auto` 为免费车道。

## 4. 能力对照（OpenMausBot 0.1.146 ↔ ds-bot 0.3.1）

✅ 已具备/等价；🟡 部分等价；❌ ds bot 缺；➕ ds bot 多出。

| 能力 | OpenMausBot | ds bot 0.3.1 | 判定 |
|---|---|---|---|
| 常驻多 Bot、每人独立指令/模型/记忆 | ✅ SOUL.md + 每线程记忆 | ✅ 每 Bot 一个 dsh Session：指令、模型、记忆、工作目录 | ✅ |
| 群聊多人协作 | ✅ rooms，不同 responder 模式 | ✅ 群聊：admin-first/@提及并行/`[PASS]`;另有**群目标引擎** `group_goal` 分阶段推进 | ➕ |
| 审批卡（Allow/Deny） | ✅ 审批级别 5 档（Ask→Full access 等），Chief 级可下放 | ✅ 审批拦截（允许一次/拒绝），群内直接出卡，与 dsh 卡片竞速 | ✅ |
| 连接应用 | ✅ Composio 500+ | ✅ ~36 应用 OAuth + 邮件全功能（搜索/读/草稿/发送） | ✅(数量少于 Market) |
| 工具桥接省 token（find_tool/use_tool） | ✅ 目录 65-74% 缩减，默认仅本地模型开 | ❌ 无 | ❌ |
| 决策模型自动路由（Jev 300ms 选谁回复） | ✅ Auto(Jev) 群路由，fail-open | 🟡 群回复靠 admin/@指定与顺序，无快速小模型裁决 | ❌ |
| 电脑控制 | ✅ 云桌面 + 本地 CUA + bot-box 沙箱（egress 代理/凭据代理） | ✅ 宿主 CUA：级别(off/view/bg/fg)、每 Bot 租约、受保护应用、接管/交还 | ✅（无云 VM 与沙箱） |
| 浏览器 | ✅ 内嵌 Chromium per-bot 分区 + CDP | ✅ 每 Bot 浏览器面板、分区、读 DOM/交互/全自动 task | ✅ |
| 定时/主动例事 | ✅ 自然语言 cron 例事 + checks + "盯住我的一天"日常简报 | ✅ 定时任务（at/every/daily/weekly/cron）；❌ 无"每日简报"级默认例事 | 🟡 |
| 健康/排障 | ✅ **Sentinel**：进程外只读扫描、签名聚合问题表、systemd/launchd 定时 | ❌ 只有被动 diagnostics.jsonl 与 reactive 修复卡 | ❌→本次已移植 |
| 语音 | ✅ 朗读回复、call 模式（按键打断）、审批语音化 | ❌ 仅接收方向（微信语音转文字、TG 音频入档） | ❌ |
| 团队一键安装/导出 | ✅ 团队 .md 包（YAML frontmatter）一键建全队 | 🟡 capabilities 可存 MCP/技能/包；无整队打包格式 | 🟡 |
| IM 接入 | ❌ 无原生 IM（靠 Phone app/companion） | ✅ Telegram/微信/飞书/Discord/Slack/QQ/钉钉/企业微信 8 平台 | ➕ |
| 办公文档 | ❌ | ➕ 内置 docx/xlsx/pptx 读写与技能 | ➕ |
| 记忆治理 | ✅ 记忆文件 + 会话记忆 | ➕ 三层记忆 + 自动 review + 面板撤销/审计上限 | ➕ |
| 目标推进 | ✅ Chief 协调 coordinate_bots | ➕ 官方 group_goal 分阶段带证据推进、学习 pass 提改技能 | ➕ |

## 5. 本次已移植的能力：Sentinel → `dsbot-sentinel/`

OpenMausBot Sentinel 的三件事：**只读**扫描数据目录、按**归一化签名**把失败聚合成
问题表、定时由 systemd/launchd 进程外运行——问题表只存归一化标题与计数
（隐私模型）。ds bot 侧没有任何等价物（只有被动记录）。

`dsbot-sentinel/`（Python 3 标准库，无依赖）逐条对齐该设计并适配 ds bot：

- 来源：ds-bot `logs/diagnostics.jsonl` 追窗重读（默认 6h）；`usage.sqlite` 只读快照；
  `state.lock` 心跳；磁盘余量。
- 输出：`~/.local/state/dsbot-sentinel/issues.jsonl`（数据目录**外**，0600，按签名
  upsert）＋ `~/.dsh/bot/workspace/SENTINEL.md`（团队工作区，整篇覆盖，Bots 可读）。
- 已安装进本部署并 cron 化（每 6 小时），cron 日志
  `dsh-superagent/.artifacts/dsbot-sentinel.log`。
- 首跑验证（2026-11-07）：26 条问题，抽样核对原始日志全部为真实记录，例如：
  - connector 上游超时（github / exa / deepwiki / wix / canva …，各 2–4 次）
  - `memory review` 输出预算不足 ×2（模型输出截断，无完整回复）
  - `computer-use masking … lossless json` 报错
  - `failed to compile structural_tag grammar: lexer error` ×4
- 用法与团队接入建议（建"健康巡检"Bot + 每日定时词）见 `dsbot-sentinel/README.md`。

## 6. 建议后续移植的 5 项（未动工，属于改插件源码/基础设施）

1. **决策模型群路由**：给群聊加 "Auto" responder——用小模型（agentgateway 的
   快模型即可）裁决未 @ 点名的消息该谁答，失败回退 admin；需在 ds-bot `groups.js` 加路由。
2. **工具桥接**（agents-agent tool bridge）：bot 会话工具目录压缩 + `find_tool`/`use_tool`，
   主要收益在小上下文的免费模型（本部署 auto-free 正是场景）。
3. **语音朗读**：TTS 走 agentgateway/云服务，回复出站时同步送一段音频（可先做
   飞书 IM 平台的语音消息出站）。
4. **每日简报级默认例事**：在 ds bot 里内建一条"盯住今天"的默认定时任务（由
   主 Bot 持有），聚合：等待审批/问题、失败任务、今天的日程/提醒。
5. **团队打包导入**（Team file）：整队 bots + 指令 + 群 + 例事的可移植 .md 打包格式，
   方便向别的 dsh 部署迁移（对齐 openmausbot-teams 的理念，格式可另定）。

## 7. 附：本票产物

- OpenMausBot 引擎配置：`~/.openmausbot/config.json`（`bob` + `auto` 两个 openai-compat 实例）
- `dsbot-sentinel/dsbot-sentinel.py` — 扫描器（已部署至 `/home/dsh/bin/dsbot-sentinel/`）
- `dsbot-sentinel/README.md` — 用法、安装、cron、团队接入
- `dsbot-sentinel/sample-issues.jsonl` — 首跑问题表样例（已含归一化标题，无原文）
- `sentinel/SENTINEL-brief-sample…` — 简报样例见团队工作区 `~/.dsh/bot/workspace/SENTINEL.md`
- OpenMausBot 本体已装在 `/opt/OpenMausBot`（数据目录 `~/.openmausbot` 使用其默认设置）

## 8. 汉化与中文输入（本轮整改）

- **UI 汉化**：`~/.openmausbot/config.json` 设 `language: "zh"`（BCP-47，简体中文），重启后 `/api/config` 返回 `language=zh`，UI 资源已包含 `zh` locale 包。验收：桌面 app `doctor` → `ready`。
- **中文输入**：根因是 WSL 缺 CJK 输入法。已装 `fcitx` + `fcitx-anthy` + `fcitx-chewing`，启动 `fcitx -d`，XMODIFIERS=`@im=fcitx`；重启 OpenMausBot 后其 X11 输入上下文 会走 XIM 走 fcitx。验收：应用内输入框可打中文。
- 备选方案：走 Web 版（Windows 浏览器访问 `http://127.0.0.1:8799`，Windows→WSL localhost 可达），有原生 IME 输入中文更可靠。

[![](https://img.shields.io/badge/powered_by-dsh-4D6BFE?style=flat-square&logo=deepseek&logoColor=white)](https://github.com/deepseek-ai/deepseek-harness)
