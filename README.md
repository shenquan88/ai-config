# AI 配置文件仓库

DeepSeek Harness 机器人的 AI 配置与运营配置仓库。

## 已接入配置

- `ASTRYX.md`：Meta Astryx 设计系统接入记录（全局 CLI、本机 Agent 技能、项目级 AGENTS.md 组件索引与验证结果）。
- `astryx-starter/`：最小可运行的 Astryx 参考工程（React 19 + Vite，无构建插件），用于验证接入并提供前端起步模板。

## 快速开始

- 本机安装 Astryx CLI 并给所有 AI Agent 装全局技能：`npm i -g @astryxdesign/cli && astryx init --user`
- 项目内接入：`npm i @astryxdesign/core @astryxdesign/theme-neutral @stylexjs/stylex && npm i -D @astryxdesign/cli && astryx init && astryx theme add neutral`
- 跑通参考工程：`cd astryx-starter && npm install && npm test && npm run build`

## 规则摘要

- 配置修改必须实际执行命令并核实输出；未测试不说已连通，工具报错不说完成。
- 前端界面优先使用 Astryx 组件与主题 token，不手写组件样式库或硬编码颜色/间距。
