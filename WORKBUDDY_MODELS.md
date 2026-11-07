# WorkBuddy 国内版模型接入（积分池）

> 把 WorkBuddy 国内版（codebuddy.cn）的模型——**含付费模型**——接入运行中的 DeepSeek Harness，
> 全部经 WorkBuddy 积分池网关路由；模型名直接标注「积分×倍率」或「免费」，用之前就能看出会不会消耗积分。

## 接入结果

| 项 | 值 |
|---|---|
| Provider id | `workbuddy` |
| 显示名 | `WorkBuddy 国内版（积分池）` |
| 协议 | OpenAI 兼容（`openai-completions`） |
| baseURL | `http://<Windows 主机 IP>:7863/v1`（当前 WSL 取到 `172.31.112.1`） |
| 凭据引用 | `WORKBUDDY_POOL_KEY`（值在 `~/.dsh/.credentials.yaml` 的 `refs`，本仓库不含钥匙值） |
| 模型数 | 31（4 个免费 + 25 个付费 + 2 个浮动/未知费率） |
| 配置方式 | DSH **设置 → 模型** 的 settings 路径写入当前 profile 的 Cordis patch；运行中的 host 热加载，**无需重启** |
| 默认模型 | **保持不变**：`oneapi / deepseek-v4.1-flash`（WorkBuddy 仅作为可选 provider 加入） |

在 DSH Web GUI（`http://127.0.0.1:3082`）的 **设置 → 模型** 里可以看到「WorkBuddy 国内版（积分池）」；
新会话输入框下方的 **选择模型** 下拉里，WorkBuddy 模型以 `WB … · 积分×…` / `WB … · 免费(×0.00)` 出现。

## 路由：DSH → 积分池网关 → WorkBuddy 账号池

```
DSH（profile: superagent）
  └─ llm-pi-ai provider `workbuddy`，api=openai-completions
       └─ http://<Windows 主机 IP>:7863/v1   ← workbuddy2api（Go 网关，OpenAI 兼容）
            └─ WorkBuddy 国内版账号池（upstream/auths 下的 3 个 cn 账号，按模型倍率扣积分）
```

- **7863 是积分池的模型出口**：`workbuddy2api` 监听 `0.0.0.0:7863`，所以 WSL 里的 DSH 能直连；
  它按上游账号池挑健康账号转发请求，并按每个模型的倍率扣积分（响应里的 `usage.credit` 即本次扣费）。
- **7864 管理台（`/accounts`）是同一个积分池的仪表盘**：`http://localhost:7864/accounts` 显示的
  账号与余额，就是 DSH 消耗的同一批国内版账号积分。它只监听 Windows 回环，**WSL 访问不到**，
  只能在 Windows 浏览器里看。
- 7865（`ai-pool-gateway` 聚合器）同样只监听回环，且只是转发层；直连 7863 已覆盖全部国内版模型，
  本方案不经过它。

即：**每调用一次付费 `WB … · 积分×…` 模型，7864 `/accounts` 里的积分就相应减少**；
`WB … · 免费(×0.00)` 的模型不扣积分。请求的模型 id 需带 `cn:` 前缀（DSH 模型 id 即目录里的真实 id）。

## 模型清单

> 倍率/上下文来自网关 `GET /v1/models`（WorkBuddy 下发的 `credits`、`context_length` 等字段）；
> 「实测」为 2026-11-07 对每个模型发一次最小请求的真实结果：48 个国内版对话模型中 31 个可服务、
> 17 个上游 503（未接入）。上游模型清单动态变化，可重新拉取后补配。

### 免费模型（4 个，不扣积分）

| 模型 id | DSH 显示名 | 积分倍率 | 计费 | 上下文 | 最大输出 | 图片 | 推理 | 工具 |
|---|---|---|---|---|---|---|---|---|
| `cn:hy3` | WB Hy3 (hy3) · 免费(×0.00) | x0.00 | 免费 | 192K | 64K | ✓ | ✓ | ✓ |
| `cn:hy3-b` | WB Hy3 (hy3-b) · 免费(×0.00) | x0.00 | 免费 | 192K | 64K | ✓ | ✓ | ✓ |
| `cn:hy3-c` | WB Hy3 (hy3-c) · 免费(×0.00) | x0.00 | 免费 | 192K | 64K | ✓ | ✓ | ✓ |
| `cn:hy4free` | WB Hy4 (hy4free) · 免费(×0.00) | x0.00 | 免费 | 960K | 64K | ✓ | ✓ | ✓ |

### 付费模型（25 个，按倍率扣积分池）

| 模型 id | DSH 显示名 | 积分倍率 | 计费 | 上下文 | 最大输出 | 图片 | 推理 | 工具 |
|---|---|---|---|---|---|---|---|---|
| `cn:hy3-x` | WB Hy3 (hy3-x) · 积分×0.05 | x0.05 | 付费 | 192K | 64K | ✓ | ✓ | ✓ |
| `cn:glm-5.3-flash` | WB GLM-5.3-Flash · 积分×0.08 | x0.08 | 付费 | 1000K | 131K | ✓ | ✓ | ✓ |
| `cn:minimax-m3.1-flash` | WB MiniMax-M3.1-Flash · 积分×0.08 | x0.08 | 付费 | 1000K | 128K | ✓ | ✓ | ✓ |
| `cn:space-bunny` | WB Space-Bunny · 积分×0.08 | x0.08 | 付费 | 1000K | 128K | ✓ | ✓ | ✓ |
| `cn:deepseek-v4.1-flash` | WB DeepSeek-V4.1-Flash · 积分×0.11 | x0.11 | 付费 | 1000K | 128K | ✓ | ✓ | ✓ |
| `cn:mimo-v2.6-pro` | WB Xiaomi MiMo-V2.6-Pro · 积分×0.13 | x0.13 | 付费 | 1000K | 128K | ✓ | ✓ | ✓ |
| `cn:fast-model` | WB 快速 · 积分×0.15 | x0.15 | 付费 | 300K | 48K | ✓ | ✓ | ✓ |
| `cn:deepseek-v4-flash` | WB Deepseek-V4-Flash · 积分×0.17 | x0.17 | 付费 | 1000K | 50K | ✓ | ✓ | ✓ |
| `cn:minimax-m2.7` | WB MiniMax-M2.7 · 积分×0.26 | x0.26 | 付费 | 200K | 48K | ✓ | ✓ | ✓ |
| `cn:deepseek-v3-2-volc` | WB DeepSeek-V3.2 · 积分×0.29 | x0.29 | 付费 | 96K | 32K | ✓ | ✓ | ✓ |
| `cn:hy4-preview-ctrl` | WB Hy4 preview (hy4-preview-ctrl) · 积分×0.29 | x0.29 | 付费 | 960K | 64K | ✓ | ✓ | ✓ |
| `cn:hy4-preview-exp` | WB Hy4 preview (hy4-preview-exp) · 积分×0.29 | x0.29 | 付费 | 960K | 64K | ✓ | ✓ | ✓ |
| `cn:hy4preview-exp1` | WB Hy4 preview (hy4preview-exp1) · 积分×0.29 | x0.29 | 付费 | 960K | 64K | ✓ | ✓ | ✓ |
| `cn:hy4preview-exp2` | WB Hy4 preview (hy4preview-exp2) · 积分×0.29 | x0.29 | 付费 | 960K | 64K | ✓ | ✓ | ✓ |
| `cn:hy4std` | WB Hy4 (hy4std) · 积分×0.29 | x0.29 | 付费 | 960K | 64K | ✓ | ✓ | ✓ |
| `cn:step-5-preview` | WB Step-5-Preview · 积分×0.33 | x0.33 | 付费 | 1000K | 64K | ✓ | ✓ | ✓ |
| `cn:kimi-k2.5` | WB Kimi-K2.5 · 积分×0.45 | x0.45 | 付费 | 256K | 32K | ✓ | ✓ | ✓ |
| `cn:balanced-model` | WB 均衡 · 积分×0.50 | x0.50 | 付费 | 300K | 48K | ✓ | ✓ | ✓ |
| `cn:deepseek-v4-pro` | WB DeepSeek-V4-Pro · 积分×0.51 | x0.51 | 付费 | 1000K | 128K | ✓ | ✓ | ✓ |
| `cn:glm-5.3` | WB GLM-5.3 · 积分×0.69 | x0.69 | 付费 | 1000K | 64K | ✓ | ✓ | ✓ |
| `cn:kimi-k2.8-preview` | WB Kimi-K2.8-Preview · 积分×0.77 | x0.77 | 付费 | 1000K | 64K | ✓ | ✓ | ✓ |
| `cn:glm-5.2` | WB GLM-5.2 · 积分×0.79 | x0.79 | 付费 | 1000K | 64K | ✓ | ✓ | ✓ |
| `cn:kimi-k3.1-pro` | WB Kimi-K3.1-Pro · 积分×0.97 | x0.97 | 付费 | 1000K | 32K | ✓ | ✓ | ✓ |
| `cn:deep-model` | WB 极致 · 积分×1.00 | x1.00 | 付费 | 300K | 48K | ✓ | ✓ | ✓ |
| `cn:kimi-k3-1` | WB Kimi-K3 · 积分×1.62 | x1.62 | 付费 | 1000K | 32K | ✓ | ✓ | ✓ |

### 浮动 / 未知费率（2 个）

| 模型 id | DSH 显示名 | 积分倍率 | 计费 | 上下文 | 最大输出 | 图片 | 推理 | 工具 |
|---|---|---|---|---|---|---|---|---|
| `cn:auto` | WB Auto · 积分浮动 | 浮动 | 浮动 | 256K | 32K | ✓ | ✓ | ✓ |
| `cn:hunyuan-chat` | WB Hunyuan-Turbos · 积分未知 | 未知 | 未知 | 128K | 8K | ✓ | — | ✓ |

COUNT used 31

### 未接入：17 个当前 503 的国内版模型

上游返回 `503 no_healthy_account`（message 内含上游 `11102 model [...] service info not found`），
即**这批账号当前拿不到该模型服务**（未开通/下架/灰度），不是 DSH 配置问题：

- `cn:glm-4.6v`
- `cn:minimax-m2.5`
- `cn:glm-4.6`
- `cn:hy4-preview-x`
- `cn:deepseek-v3-0324-lkeap`
- `cn:deepseek-v3-1`
- `cn:deepseek-v3-1-lkeap`
- `cn:deepseek-v3-1-volc`
- `cn:kimi-k2-thinking`
- `cn:glm-5.0-turbo`
- `cn:deepseek-r1-0528`
- `cn:deepseek-r1-0528-lkeap`
- `cn:deepseek-v3-0324`
- `cn:default-1.1`
- `cn:default-1.2`
- `cn:hunyuan-2.0-instruct`
- `cn:kimi-k2-instruct-taiji`

池子恢复后可这样复核并补配（拿到 200 就说明可用了）：

```bash
HOSTIP=$(ip route show default | awk '{print $3}')          # Windows 主机 IP
KEY_PATH=~/.dsh/.credentials.yaml                             # 仅示意：实际用已配置的凭据引用
# 列出上游当前下发的全部模型 id
curl -s -H "Authorization: Bearer $WORKBUDDY_POOL_KEY" "http://$HOSTIP:7863/v1/models" \
  | jq -r '.data[].id' | grep '^cn:' | sort

# 逐个探测某个未接入模型（200 = 恢复可用；503 = 仍不可用）
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $WORKBUDDY_POOL_KEY" -H 'Content-Type: application/json' \
  -X POST "http://$HOSTIP:7863/v1/chat/completions" \
  -d '{"model":"cn:glm-4.6","messages":[{"role":"user","content":"hi"}],"max_tokens":8}'
```

### 未接入：3 个国内版媒体模型

`cn:hunyuan-image-alpha-edit`（图生图）、`cn:kling-video-v3`（文/图生视频）、
`cn:minimax-video-h3`（文/图生视频）——非对话模型，DSH 文本链路不用，未配置。

### 未接入：23 个 `global:*` 国际版模型

网关同时下发国际版（workbuddy.ai）模型，但对应账号当前余额为 0，本方案只接国内版 `cn:*`。

## 监控积分消耗

DSH 使用 7863 的全局钥匙，7864 管理台没有「按 key」的细分统计，因此积分监控用这几处：

| 目的 | 方式 |
|---|---|
| 单次调用扣了多少 | 响应里的 `usage.credit`（免费模型为 `0`）；`usage.quota` 还有模型配额百分比与重置时间 |
| 累计 / 按模型 | `GET /v1/stats` → `total.credit`、各模型 `credit` / `credit_per_req` / 倍率原值 |
| 账号余额 | `GET /status` → `accounts[].credits`（上游定时任务刷新的快照，有滞后） |
| 直观仪表盘 | Windows 浏览器打开 `http://localhost:7864/accounts`（同一账号池） |

```bash
HOSTIP=$(ip route show default | awk '{print $3}')          # Windows 主机 IP（会变）
BASE="http://$HOSTIP:7863/v1"

# 累计扣费（total.credit）与各模型明细
curl -s -H "Authorization: Bearer $WORKBUDDY_POOL_KEY" "$BASE/stats" | jq '.total.credit, .models'

# 账号余额
curl -s -H "Authorization: Bearer $WORKBUDDY_POOL_KEY" "$BASE/status" | jq '.accounts[] | {nickname, credits}'
```

**倍率 vs 实际扣费**：`credits`（如 `x0.11` / `x0.29`）是网关声明的**倍率**，实际扣费按 token 量折算，
还有缓存折扣（实测缓存命中率可达 60%–77%）。因此：

- 小请求的 `usage.credit` 可能因取整/缓存显示为 `0`，但 `/v1/stats` 的模型累计仍会增长；
- **不要用倍率 × token 精确预估费用**，展示时标明「付费 / 倍率」即可；
- 免费模型 `x0.00` 恒不扣；`cn:auto` 倍率随实际路由浮动；`cn:hunyuan-chat` 上游未下发倍率，按「未知」保守对待。

接入与联调期间实测花费约 1.5–2 积分（3 个国内版账号余额约 **1292 / 1354 / 1455**，合计约 4100 分，影响可忽略）。

## 验证

- **GUI（截图证据，见下）**：运行中的 GUI 设置 → 模型出现「WorkBuddy 国内版（积分池）」，模型下拉出现 31 个
  `WB … · 积分×… / 免费(×0.00)` 模型；**未重启 dsh 进程**。
- **端到端**：联调期间通过该 provider 跑过真实 DSH agent 回合（DSH 会话的模型切换记录与池
  `GET /v1/stats` 的请求/扣费记录可对上），证明 DSH → 7863 → 账号池整条链路可用；付费模型的
  真实扣费也在池侧验证过（`cn:hy4std` +0.12、`cn:deepseek-v4-pro` +0.07、`cn:glm-5.3` +0.03 积分）。
- **默认模型**：联调时曾临时把默认模型切到 WorkBuddy 模型；因 `cn:deepseek-v4-flash`、`cn:deep-model`
  出现间歇性 503，最终已回退为原默认 `oneapi / deepseek-v4.1-flash`（与接入前一致）。

## 限制与注意事项

1. **Windows 主机 IP 会变**：`baseURL` 里的 `172.31.112.1` 由 `ip route show default | awk '{print $3}'` 取得，
   Windows/WSL 重启后可能不同；变了就更新 provider 的 `baseURL`（热生效）。
2. **7864 / 7865 从 WSL 不可达**（Windows 回环绑定，未提权做 portproxy）：积分面板只能在 Windows 看；
   但 7863 与它们是同一个账号池，扣费可用 `usage.credit` / `/v1/stats` 验证。
3. **Windows 上的 WorkBuddy 栈必须运行**（`wb2api.exe` 监听 7863）；主机或该服务停了，WorkBuddy 模型全部不可用。
4. **只接了国内版 `cn:*`**：23 个 `global:*` 国际版模型（账号余额 0）与 3 个图像/视频媒体模型未接入。
5. **17 个 `cn:*` 模型当前上游 503**，未列入配置；模型清单为上游动态下发，可能增减。
6. **推理模型的 reasoning token 计入 `max_tokens`**：给推理模型留足输出预算（建议 ≥512），
   否则可能出现 `finish_reason=length` 且拿不到最终答案。
7. **响应里的 `model` 会去掉 `cn:` 前缀**（如返回 `hy3`），不要用它反查配置。
8. **仅 OpenAI 协议**：`/v1/messages`（Anthropic 形态）在该端口 404。
9. 上游偶发 `503`（`no_healthy_account`）与账号冷却属正常波动；重试或换模型即可，不要当配置错误。
10. 若轮换了上游全局钥匙，只需更新 `WORKBUDDY_POOL_KEY` 的凭据值，provider 配置不用动。

## 配置片段（不含钥匙值）

```yaml
providers:
  workbuddy:
    displayName: WorkBuddy 国内版（积分池）
    apiKeyEnv: WORKBUDDY_POOL_KEY        # 凭据引用，值在 ~/.dsh/.credentials.yaml
    api: openai-completions
    baseURL: http://<Windows 主机 IP>:7863/v1
    defaultContextWindow: 262144
    defaultMaxTokens: 32768
    compat:
      supportsDeveloperRole: true
      supportsStore: true
      supportsReasoningEffort: true
      supportsUsageInStreaming: true
      supportsFinishReason: true
      maxTokensField: max_tokens
      requiresReasoningContentOnAssistantMessages: false
    models:
      - id: cn:hy3                      # 免费
        name: WB Hy3 (hy3) · 免费(×0.00)
        contextWindow: 192000
        maxTokens: 64000
        input: [text, image]
        reasoningEfforts: { low: low, high: high }
      - id: cn:balanced-model           # 付费 x0.50
        name: WB 均衡 · 积分×0.50
        contextWindow: 300000
        maxTokens: 48000
        input: [text, image]
        reasoningEfforts: { low: low, high: high, max: max }
      # ……其余 29 个模型同格式，id / name / contextWindow / maxTokens 见上表
```

## 视觉证据

**Before（接入前基线）** — 配置修订 `f134ece89264018f938019dd5e8c410112eba5ef909b5c7609a602469f28b349`
（2026-11-07 08:25，7 个 provider）：

![before: Settings → Models](docs/images/workbuddy-models/before-models.png)

![before: composer model picker](docs/images/workbuddy-models/before-picker.png)

**After（接入后）** — 配置修订 `fd5ce074821f69877d11f9777c8390ef76fdf07cca449feea50b97ece0c28688`
（2026-11-07 10:10，8 个 provider，新增「WorkBuddy 国内版（积分池）」与 31 个 WB 模型）：

![after: Settings → Models](docs/images/workbuddy-models/after-models.png)

![after: composer model picker](docs/images/workbuddy-models/after-picker.png)

截图条件：Windows ego-browser，CSS 视口 1280×960、浅色主题，同场景同视口前后对比；截图中无密钥明文。

[![](https://img.shields.io/badge/powered_by-dsh-4D6BFE?style=flat-square&logo=deepseek&logoColor=white)](https://github.com/deepseek-ai/deepseek-harness)
