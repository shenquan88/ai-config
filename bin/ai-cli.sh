#!/usr/bin/env bash
# ai-cli.sh — 从 WSL 调用 Windows 侧 AI CLI（claude / codex / gemini）。
# 用法: ai-cli.sh <claude|codex|gemini> "<prompt>" [超时秒数]
#
# 为什么走临时 .bat：
#   1) WSL 当前目录是 \\wsl.localhost\...，cmd.exe 不支持 UNC 路径，必须 cd /d 到 C:\
#   2) 直接 cmd.exe /c "..." 时引号会被 Windows 参数解析吃掉
#   3) prompt 通过 stdin 管道送入，避免任何转义问题
#
# 默认行为（推荐）：不给任何覆盖，直接沿用各 CLI 自己的配置。
#   三个 CLI 的配置都指向本机 magpie 路由 127.0.0.1:3425 的免费分组
#   （claude/codex -> group/free-first，gemini -> group/cheap-first）。
#   => 只要 magpie 在跑（D:\Downloads\magpie-windows-amd64.exe），就是 auto-free。
#
# 可选覆盖（想绕开 magpie 直连本机 agentgateway 免费车道时）：
#   AI_CLI_USE_GATEWAY=1 AI_CLI_GATEWAY=http://127.0.0.1:20080 \
#   AI_CLI_CLAUDE_MODEL=free-cohere-mini AI_CLI_CODEX_MODEL=free-cohere-mini \
#   ai-cli.sh claude "..."
set -uo pipefail

CLI="${1:?usage: ai-cli.sh <claude|codex|gemini> <prompt> [timeout_seconds]}"
PROMPT="${2:-}"
TMO="${3:-300}"

USE_GW="${AI_CLI_USE_GATEWAY:-0}"
GW_BASE="${AI_CLI_GATEWAY:-http://127.0.0.1:20080}"
CLAUDE_MODEL="${AI_CLI_CLAUDE_MODEL:-free-cohere-mini}"
CODEX_MODEL="${AI_CLI_CODEX_MODEL:-free-cohere-mini}"

WT="/mnt/c/Windows/Temp"
TAG="ai-cli-$$-$RANDOM"
P="$WT/$TAG.prompt"
B="$WT/$TAG.bat"
O="$WT/$TAG.out"
W() { printf 'C:\\Windows\\Temp\\%s' "$1"; }

printf '%s' "$PROMPT" > "$P"
: > "$O"

{
  printf '@echo off\r\n'
  printf 'cd /d C:\\Windows\\Temp\r\n'
  if [ "$USE_GW" = "1" ]; then
    case "$CLI" in
      claude)
        printf 'set ANTHROPIC_BASE_URL=%s\r\n' "$GW_BASE"
        printf 'set ANTHROPIC_AUTH_TOKEN=local-gateway\r\n'
        printf 'set ANTHROPIC_MODEL=%s\r\n' "$CLAUDE_MODEL"
        printf 'type "%s" | claude -p --model "%s" >"%s" 2>&1\r\n' \
          "$(W "$TAG.prompt")" "$CLAUDE_MODEL" "$(W "$TAG.out")" ;;
      codex)
        printf 'type "%s" | codex exec --skip-git-repo-check -c mcp_servers={} -c model="%s" -c model_provider="gateway" -c model_providers.gateway.name="gateway" -c model_providers.gateway.base_url="%s/v1" -c model_providers.gateway.wire_api="responses" -c model_providers.gateway.experimental_bearer_token="local" - >"%s" 2>&1\r\n' \
          "$(W "$TAG.prompt")" "$CODEX_MODEL" "$GW_BASE" "$(W "$TAG.out")" ;;
      gemini)
        printf 'set GEMINI_API_KEY=local-gateway\r\n'
        printf 'set GOOGLE_GEMINI_BASE_URL=%s\r\n' "$GW_BASE"
        printf 'set GEMINI_CLI_TRUST_WORKSPACE=true\r\n'
        printf 'type "%s" | gemini -p "" --skip-trust >"%s" 2>&1\r\n' \
          "$(W "$TAG.prompt")" "$(W "$TAG.out")" ;;
      *) echo "未知 CLI: $CLI（可用: claude|codex|gemini）" >&2; exit 2 ;;
    esac
  else
    case "$CLI" in
      claude)
        printf 'type "%s" | claude -p >"%s" 2>&1\r\n' \
          "$(W "$TAG.prompt")" "$(W "$TAG.out")" ;;
      codex)
        printf 'type "%s" | codex exec --skip-git-repo-check -c mcp_servers={} - >"%s" 2>&1\r\n' \
          "$(W "$TAG.prompt")" "$(W "$TAG.out")" ;;
      gemini)
        printf 'set GEMINI_API_KEY=magpie\r\n'
        printf 'set GOOGLE_GEMINI_BASE_URL=http://127.0.0.1:3425\r\n'
        printf 'set GEMINI_MODEL=%s\r\n' "${AI_CLI_GEMINI_MODEL:-group/cheap-first}"
        printf 'set GEMINI_CLI_TRUST_WORKSPACE=true\r\n'
        printf 'type "%s" | gemini -p "" --skip-trust >"%s" 2>&1\r\n' \
          "$(W "$TAG.prompt")" "$(W "$TAG.out")" ;;
      *) echo "未知 CLI: $CLI（可用: claude|codex|gemini）" >&2; exit 2 ;;
    esac
  fi
} > "$B"

timeout "$TMO" /mnt/c/Windows/System32/cmd.exe /c "$(W "$TAG.bat")" >/dev/null 2>&1
rc=$?
cat "$O" 2>/dev/null
rm -f "$P" "$B" "$O" 2>/dev/null
exit "$rc"
