# Anthropic Knowledge Work Plugins 配置

> 主题：Anthropic 开源 knowledge-work-plugins，让 Claude 从聊天机器人变身职场搭档。

## 配置事实（已实测验证）

- 来源仓库：https://github.com/anthropics/knowledge-work-plugins
- Marketplace：`knowledge-work-plugins`（source: github `anthropics/knowledge-work-plugins`）
- 添加命令：`claude plugin marketplace add anthropics/knowledge-work-plugins`
- 已安装插件：`customer-support@knowledge-work-plugins`（version 1.3.0，scope: user，status: enabled）
- 安装命令：`claude plugin install customer-support@knowledge-work-plugins`
- customer-support 组件清单（v1.3.0）：Skills 5（customer-escalation、customer-research、draft-response、kb-article、ticket-triage），MCP servers 8（slack、intercom、hubspot、guru、atlassian、notion、google calendar、gmail），projected always-on token cost 约 379。

## 验证结果

- `claude plugin marketplace add anthropics/knowledge-work-plugins` → √ Successfully added marketplace: knowledge-work-plugins
- `claude plugin install customer-support@knowledge-work-plugins` → √ Successfully installed plugin: customer-support@knowledge-work-plugins (scope: user)
- `claude plugin list` → customer-support@knowledge-work-plugins … Status: √ enabled
- `claude plugin details customer-support@knowledge-work-plugins` → component inventory 正常

## 使用方式

- Claude Code：`claude plugin install <plugin>@<marketplace>`，启用后 skills 按需触发，slash command 如 `/<plugin>:<command>` 可用。
- Cowork：`/plugin load customer-support --config ./my-company.yaml`。

## 个性化定制

- 切换连接器：编辑插件 `.mcp.json`，把 `~~category` 占位符指向公司具体工具（如 `~~support platform` → Intercom / Zendesk / HubSpot Service Hub）。
- 注入公司上下文：把公司内部术语、组织结构、流程写入对应 skill 文件。
- 调整工作流：按团队实际流程修改 skill instructions。
- 新建插件：可用 `cowork-plugin-management` / `claude plugin init` 创建。

## 后续

- 按职能目录挑选更多插件：`claude plugin install <plugin>@<marketplace>`。
- 从小工作流试点开始，跑通后推广到团队关键工作流。
