# Magpie / Qoder 免费模型接入（DSH + mausbot）

> 背景：Qoder（IDE / CLI）**不对外提供模型 API**——`qodercli login` 只有账号登录，没有 API Key 模式，
> 后端是产品自己的 `openapi.qoder.com.cn`。Qoder 实际是「客户端」：它的模型来自本机 **Magpie** 网关
> （`http://127.0.0.1:3425/v1`）。所以要把「Qoder 里的免费模型」接进 DSH / mausbot，接的是 Magpie 的网关。

## 接入结果

| 项 | 值 |
|---|---|
| 网关 | Magpie，`http://<Windows 主机 IP>:3425/v1`（监听 `0.0.0.0`，WSL 可直连，**不需要代理**） |
| 鉴权 | Magpie 网关 caller key（存在 `C:\Users\Administrator\.config\magpie\caller-keys.json`，名字 `Magpie`） |
| DSH | provider `magpie`，显示名「Magpie 免费模型（Qoder 同源）」，20 个已实测可用的免费模型 |
| mausbot | 实例 `magpie-free`「Magpie 免费模型（Qoder 同源 · 已实测可用 20 个）」，默认 `group/free-first` |
| 计费 | 免费项 `cost = 0`（响应 `usage.cost` / `pricing` 均为 0） |

Magpie 目录里有 393 个模型，其中免费相关 57 项（`group/free-first` 路由组 + 55 个 `*:free`）。
逐条实测后 **20 个可用**；其余 404（免费版已下架）/429（免费档限速）/超时，未接入。

## 可用模型（2026-11-08 实测，20 个）

| 模型 id | 名称 | 上下文 | 最大输出 | 工具 |
|---|---|---|---|---|
| `group/free-first` | Free First | 1048K | 943K | ✓ |
| `group/cheap-first` | 便宜优先 | 1049K | 262K | ✓ |
| `auto/nemotron-3-ultra-550b-a55b:free` | Nemotron 3 Ultra (free) | 1000K | 65K | ✓ |
| `auto/nemotron-3.5-lightning:free` | Nemotron 3.5 Lightning (free) | 1000K | 65K | ✓ |
| `openrouter-2/nvidia/nemotron-3-ultra-550b-a55b:free` | Nemotron 3 Ultra (free) | 1000K | 65K | ✓ |
| `openrouter-3/nvidia/nemotron-3.5-lightning:free` | Nemotron 3.5 Lightning (free) | 1000K | 65K | ✓ |
| `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | Nemotron 3 Ultra (free) | 1000K | 65K | ✓ |
| `openrouter/nvidia/nemotron-3.5-lightning:free` | Nemotron 3.5 Lightning (free) | 1000K | 65K | ✓ |
| `auto/gemma-4-26b-a4b-it:free` | Gemma 4 26B A4B  (free) | 262K | 32K | ✓ |
| `auto/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Nemotron 3 Nano Omni (free) | 256K | 65K | ✓ |
| `auto/north-mini-code:free` | North Mini Code (free) | 256K | 64K | ✓ |
| `openrouter-2/cohere/north-mini-code:free` | North Mini Code (free) | 256K | 64K | ✓ |
| `openrouter-2/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Nemotron 3 Nano Omni (free) | 256K | 65K | ✓ |
| `openrouter-3/cohere/north-mini-code:free` | North Mini Code (free) | 256K | 64K | ✓ |
| `openrouter/cohere/north-mini-code:free` | North Mini Code (free) | 256K | 64K | ✓ |
| `openrouter/nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | Nemotron 3 Nano Omni (free) | 256K | 65K | ✓ |
| `auto-free/auto:free` | Auto Router (free) | 128K | 16K | ✓ |
| `auto/lfm-2.5-2.6b:free` | LFM2.5-2.6B (free) | 65K | 8K | ✓ |
| `openrouter-2/liquid/lfm-2.5-2.6b:free` | LFM2.5-2.6B (free) | 65K | 8K | ✓ |
| `openrouter/liquid/lfm-2.5-2.6b:free` | LFM2.5-2.6B (free) | 65K | 8K | ✓ |

> `group/free-first` 是「免费优先」路由组：按可用性与限速自动挑一个免费模型，日常用最省心。
> `group/cheap-first` 是「便宜优先」路由组，**可能计费**，因此显示名标注为「可能计费」。

## DSH 侧配置（不含钥匙值）

```yaml
providers:
  magpie:
    displayName: Magpie 免费模型（Qoder 同源）
    api: openai-completions
    apiKeyEnv: MAGPIE_GATEWAY_KEY          # 值在 ~/.dsh/.credentials.yaml refs，不入库
    baseURL: http://<Windows 主机 IP>:3425/v1
    defaultContextWindow: 131072
    defaultMaxTokens: 16384
    compat:
      supportsDeveloperRole: true
      supportsStore: false
      supportsReasoningEffort: true
      supportsUsageInStreaming: true
      maxTokensField: max_tokens
    models: [ 20 项，见上表 ]
```

生效方式与 WorkBuddy 一致：走 DSH 设置服务的 settings 写入路径，运行中的 host 热加载、**无需重启**。

## mausbot 侧配置

```json
"magpie-free": {
  "driver": "openai-compat",
  "displayName": "Magpie 免费模型（Qoder 同源 · 已实测可用 20 个）",
  "access": "api",
  "config": {
    "key": "<Magpie caller key>",
    "url": "http://<Windows 主机 IP>:3425/v1",
    "managedModels": ["group/free-first", "group/cheap-first", "..."]
  }
}
```

## 验证

- Magpie `/v1/models`（带 caller key）→ 200，393 个模型；`group/free-first`、`group/cheap-first` 均在。
- 逐模型实测：`group/free-first` 与 `auto/nemotron-3.5-lightning:free` 等 20 个返回 200，`usage.cost = 0`，
  带工具调用参数也正常。
- DSH 运行中的 host：`session/modelCatalog` 的 `routableProviders` 含 `magpie`，该组 20 个模型；
  `settings/describe` 里 `magpie.baseURL` 如上。
- mausbot：`GET /api/instances` 中 `magpie-free` 状态 `available`、20 个模型、默认 `group/free-first`。

## 限制

1. **Windows 主机 IP 会变**（WSL 默认网关，如 `172.31.112.1`）：变了要同步改 DSH provider 的 `baseURL`
   与 mausbot 实例的 `url`（8766 代理只覆盖 WorkBuddy，不覆盖 Magpie）。
2. **免费档有速率限制**（OpenRouter 系免费模型常见 429 free-models-per-...），高峰期会失败，重试或换模型。
3. 免费模型清单随上游变化：本次 57 个免费项里只有 20 个当时可用，建议定期重跑盘点。
4. Qoder 本身没有对外模型 API；本方案用的是 Magpie 的网关键，与 Qoder 的登录态无关。
5. `group/cheap-first` 可能产生费用，未按免费对待。
