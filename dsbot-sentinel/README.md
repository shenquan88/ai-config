# dsbot-sentinel

OpenMausBot 的 **Sentinel**（健康扫描器）能力移植到 **ds bot**（DeepSeek Harness 的 ds-bot
团队部署）的一个可运行落地件：只读扫描 ds bot 的数据目录，把反复出现的失败聚合成
"问题表"，并把一份不含内容的简报写到团队的共享工作区，让每个 Bot（和用户）醒来就能读到。

## 是什么

- **对齐 OpenMausBot 的设计**（其 `docs/sentinel.md`）：
  - 所有来源只读打开，绝不修改被读取的数据目录；
  - 失败按**归一化签名**聚合（路径、数字、UUID、URL、引号内容先替换再哈希），
    例如 "MEMORY.md would have 4085/4000 characters" 与 "would have 4049/4000" 归为一条；
  - 问题表只存**引用与短归一化标题**，从不存原始日志文本（隐私模型）；
  - `issues.jsonl` **按签名 upsert**：count/firstAt/lastAt 原地更新，每次出现只数一次；
    `evidenceRef` 指回来源，需要时人工回看原始记录；
  - 问题表放在数据目录**之外**（`~/.local/state/dsbot-sentinel/`，XDG state 规范）。
- **与 OMB 的差异（有意的简化）**：
  - 以 ds bot 现有的 `~/.dsh/bot/logs/diagnostics.jsonl` 为主来源（ds-bot 只被动记日志、
    无检测循环，见仓库对比文档§health scanner）；
  - 附带只读读 `usage.sqlite`（24h 调用次数/tokens，只计数不读内容）、
    `state.lock` 心跳（dsh 是否在刷新团队锁）、磁盘余量;
  - 简报 `SENTINEL.md` 写入团队工作区 `~/.dsh/bot/workspace/`——这是唯一写进数据目录的
    文件，目的就是让团队能读到;原始问题表仍在数据目录外。

## 用法

```sh
python3 dsbot-sentinel.py                # 默认参数：6h 窗口，写出简报
python3 dsbot-sentinel.py --json         # 输出一个 JSON 摘要
python3 dsbot-sentinel.py --lookback-minutes 720   # 回看 12 小时
python3 dsbot-sentinel.py --quiet        # 用于 cron
# 退出码：0 成功；2 参数错误；1 扫描失败（stderr 带原因）
```

输出：

| 文件 | 位置 | 内容 |
|---|---|---|
| `issues.jsonl` | `~/.local/state/dsbot-sentinel/` | 按签名 upsert 的问题表（模式 0600） |
| `SENTINEL.md` | `~/.dsh/bot/workspace/` | 近 6h 问题 + 24h 用量 + 机器状态简报（整篇覆盖） |

## 安装（cron，每 6 小时）

```sh
sudo install -D -m 755 dsbot-sentinel.py /home/dsh/bin/dsbot-sentinel/dsbot-sentinel.py
crontab 添加:
30 */6 * * * /home/dsh/bin/dsbot-sentinel/dsbot-sentinel.py --quiet --lookback-minutes 360 >> /home/dsh/dsh-superagent/.artifacts/dsbot-sentinel.log 2>&1
```

## 让团队真正用起来（建议，需团队内创建）

请主 Bot（Chief）或用户在 ds-bot 里建一个"健康巡检"Bot，并在其对话内建一条
Scheduled task（定时任务，ds-bot settings → Scheduled tasks），提示词：

```text
每天 08:30 读取工作区 SENTINEL.md（状态简报）。若有 [high] 条目或 state.lock
心跳超过 3 分钟，向用户简要报告问题与建议处理；一切正常时不打扰，只回一句"巡检正常"。
```

这样人就不再需要自己看日志，也与 OMB Sentinel "Issue 由人复核"的定位一致。

## 已做的首次验证（2026-11-07）

首跑 26 条问题被识别，其中真实发现包括：
connector 上游批量超时（github/exa/deepwiki/wix/canva …）、memory review 输出预算不足、
computer-use 掩码报错、structural_tag grammar 编译失败等——都是 diagnostics.jsonl 里
真实存在的记录（明细见 issues.jsonl；原始行见 ~/.dsh/bot/logs/diagnostics.jsonl）。

## 边界（诚实声明）

- v1 只扫 diagnostics 级失败与机器状态，不逐条比对 Session 日志里的工具调用成败
  （OMB 系 messages.db 逐行扫描，我们还没有等价的容易只读打开的数据库）；这写在
  对比文档的"后续"里。
- 心跳检测以 `state.lock` 的 mtime 为准（进程名是 `node`，按名 grep 会误报）。
- 简报只写次数与归一化标题，不写用户消息、密钥或会话内容；问题表同样如此。

[![](https://img.shields.io/badge/powered_by-dsh-4D6BFE?style=flat-square&logo=deepseek&logoColor=white)](https://github.com/deepseek-ai/deepseek-harness)
