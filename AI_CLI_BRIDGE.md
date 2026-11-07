# Windows AI CLI 桥接（claude / codex / gemini）

目标：让 DeepSeek harness 的 worker 和 Bot 团队都能在自己干活时调用 Windows 侧的
Claude Code、Codex、Gemini CLI，模型全部走本机免费路由，零 API 费用。

## 用法

```bash
/home/dsh/bin/ai-cli.sh claude "把这段代码改成异步" 300
/home/dsh/bin/ai-cli.sh codex  "给这个仓库补单元测试" 300
/home/dsh/bin/ai-cli.sh gemini "总结这个文件" 300
```

参数：`<claude|codex|gemini> <prompt> [超时秒数，默认 300]`。
输出直接打到 stdout（各 CLI 自己的原始输出）。

## 为什么需要这层桥接

1. WSL 的当前目录是 `\\wsl.localhost\...`，`cmd.exe` 不支持 UNC 路径，必须 `cd /d` 到 `C:\`。
2. 直接 `cmd.exe /c "claude -p '...'"` 时引号会被 Windows 参数解析吃掉。
3. 所以脚本把命令写成临时 `.bat`，prompt 写临时文件后用 `type file | cli` 走 stdin 送入。

## 模型与后端（auto-free）

三个 CLI 的配置都指向本机 magpie 路由 `http://127.0.0.1:3425`：

| CLI | 模型 | 配置文件 |
|---|---|---|
| claude | `group/free-first[1m]` | `~/.claude/settings.json` |
| codex  | `group/free-first` | `~/.codex/config.toml` |
| gemini | `group/cheap-first` | `~/.gemini/settings.json` + `.env` |

magpie 启动：`start "" "C:\Users\Administrator\Downloads\magpie-windows-amd64.exe"`
（已有 HKCU Run 自启项；magpie 不在跑时三个 CLI 全部连接失败。）

## 实测（2026-11-07）

| CLI | 命令 | 结果 |
|---|---|---|
| claude | `ai-cli.sh claude "What is 2+2?"` | `4` ✅ |
| codex  | `ai-cli.sh codex "What is 2+2?"` | `4` ✅ |
| gemini | `ai-cli.sh gemini "What is 2+2?"` | `4` ✅ |

已知噪声（不影响结果）：

- claude 会先打一行 `[claude-code:unrecognized_model] {"model":"group/free-first[1m]"}`。
  原因是 magpie 组名带 `[1m]` 上下文标记，Claude Code 不认这个别名；调用本身照常成功。
- gemini 需要可信目录，脚本已带 `--skip-trust` 并设 `GEMINI_CLI_TRUST_WORKSPACE=true`。
- codex 启动会尝试连配置里的 MCP 服务器（多数需鉴权），脚本默认加 `-c mcp_servers={}`
  跳过它们以避免数分钟启动延迟；需要 MCP 时把该参数去掉。

## 可选：绕开 magpie 直连 agentgateway

```bash
AI_CLI_USE_GATEWAY=1 AI_CLI_GATEWAY=http://127.0.0.1:20080 \
AI_CLI_CLAUDE_MODEL=free-cohere-mini AI_CLI_CODEX_MODEL=free-cohere-mini \
  ai-cli.sh claude "问题"
```

说明：agentgateway 的 `/v1/messages`（Anthropic 协议）和 `/v1/responses`（OpenAI Responses）
都可用，免费车道 `free-cohere-mini` 实测能出字；但 claude -p 走该路径会挂住不返回
（免费车道的流式内容块与工具调用不满足 Claude Code 要求），因此默认仍走 magpie。

## Bot 团队

团队记忆 `~/.dsh/bot/memory/team/MEMORY.md` 已登记该脚本，Bot 用 bash 工具直接调用即可。
