# Astryx 设计系统接入记录

> Meta 开源的 React 19 + StyleX 设计系统接入配置。
> 来源：https://github.com/meta/astryx（视频里展示的 github.com/astryx/astryx 是占位、已 404；实际仓库为 meta/astryx）。当前版本 `0.7.10`（Beta，MIT）。

## 接入内容（已实测）

1. **全局 CLI 安装**：`npm i -g @astryxdesign/cli`（CLI 0.7.10 + Core 0.7.10）。注意：未加 `--scope` 的 `astryx` 包与本设计系统无关，必须使用 `@astryxdesign/*`。
2. **本机 Agent 技能**：`astryx init --user` 已写入 `~/.agents/skills/astryx/SKILL.md` 并链接到 `~/.claude/skills/astryx`，让本机所有 AI 编程 Agent 都能读到 Astryx 组件索引与设计规范。
3. **项目级 AGENTS.md 组件索引**：在 `astryx-starter/` 工程内运行 `astryx init`，向 `AGENTS.md`/`GEMINI.md` 写入受管块 `<!-- ASTRYX:START -->...<!-- ASTRYX:END -->`（174 个组件、CLI 工作流与 RULES），让 Agent 清楚有哪些组件可用、不瞎写样式。
4. **最小可运行参考工程** `astryx-starter/`：React 19 + Vite，无需构建插件，仅导入预编译 CSS 与主题即可。用于验证接入并作为前端起步模板。

## 关键事实（实测验证）

- 包结构：`@astryxdesign/core`（组件）、`@astryxdesign/theme-neutral`（Neutral 主题）、`@stylexjs/stylex`（peer 依赖）、React 19.3.1。
- 组件索引：`astryx component --list` 共 **78 个分组、174 个导出**（Button、Card、Heading、Text、Badge、Stack、TextInput、Banner、Divider、Layout 等）。带 `--json` 可导出清单。
- 主题自带深色模式：Neutral 主题 `neutralTheme` 内建 light/dark 双套 token，无需额外配置即支持深色模式。
- 安装脚本被沙箱拦截（`npm warn install-scripts`）但 CLI 功能完整，`astryx doctor` 通过。

## 接入流程（复刻到新工程）

```bash
# 1) 全局 CLI + 本机 Agent 技能（每台机器一次）
npm i -g @astryxdesign/cli
astryx init --user

# 2) 项目内（每个前端工程）
npm i @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex
npm i -D @astryxdesign/cli
astryx init                                  # 写入 AGENTS.md 组件索引
astryx theme add neutral                     # 生成 src/astryx-themes.js

# 3) 入口（main.jsx / main.tsx）一次性接好，否则组件无样式
import '@astryxdesign/core/reset.css';
import '@astryxdesign/core/astryx.css';
import {themes, defaultThemeSlug} from './astryx-themes';
import {Theme} from '@astryxdesign/core/theme';
import App from './App.jsx';

<Theme theme={themes[defaultThemeSlug]}><App /></Theme>
```

## 验证结果

`astryx-starter/` 工程内已跑通（详见该目录）：

- `astryx doctor` → **pass 19 / warn 2 / fail 0**（warnings：外部 Figtree 字体需联网加载、未使用模板脚手架，均不影响渲染）。
- `npm test` → **3 个 SSR 渲染用例全部通过**：Button/Card/Stack/Heading/Text/Badge/TextInput 正常渲染、Theme 注入 Neutral token。
- `npm run build` → Vite 生产构建成功（`dist/` 产出 JS + 284KB CSS）。

## AI Agent 规则（来自 Astryx）

- 不写裸 `<div>`/`<span>`，布局与间距交给组件。
- 优先用组件 props 控制样式，其次用主题 token（`var(--color-*|--spacing-*|--radius-*)`）；禁止硬编码 hex/px。
- 配色与自定义颜色一律走主题，不写 `:root` 覆盖。
- 每个页面从模板起步：`astryx build "<想法>"` → `astryx template <name> <path>`，不要从零手写。
- 交付前跑 `astryx doctor --built <dir>`，不通过不交付。

## 后续

- 需要更多主题：`astryx theme add <slug>`；要改主题源码：`astryx theme eject <slug>`（仅 fork 源码时才用）。
- 查组件用法：`astryx component <Name>`；查文档：`astryx docs <topic>`（principles、tokens、theme、styling-overview 等）。

[![](https://img.shields.io/badge/powered_by-dsh-4D6BFE?style=flat-square&logo=deepseek&logoColor=white)](https://github.com/deepseek-ai/deepseek-harness)
