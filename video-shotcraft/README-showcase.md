# video-shotcraft 微信小程序视频 —— 词元闯关版

本目录在 `video-shotcraft/remotion-template`（Remotion 电影感产品视频 skill 模板）基础上，
新增了一个面向「词元闯关」微信小程序的 **video-shotcraft 介绍视频** 合成。

## 交付物

- 合成 ID：`VideoShotcraftShowcase`
- 时长：1085 帧 @ 30fps ≈ 36.2 秒，1920×1080
- 产物：`video-shotcraft/remotion-template/out/video-shotcraft-showcase.mp4`
- 预览静帧（证据）：`video-shotcraft/remotion-template/out/evidence2/*.png`
  - `disclaimer.png` 片头免责声明（本视频仅供学习交流，请勿用于非法用途）
  - `title.png` 标题卡（用 video-shotcraft 做电影感宣传视频）
  - `github.png` video-shotcraft GitHub 项目页（faux 还原）
  - `python.png` Python API 调用示例（含注释 `# 当前有104个镜头`）
  - `shotlist.png` 镜头卡清单 1–104（两栏自动滚动）
  - `closer.png` 结尾卡（词元闯关·AI 背单词闯关）

## 视频对应核心内容（按需求「二、视频相应核心内容」逐条实现）

1. 片头免责声明：**本视频仅供学习交流，请勿用于非法用途**（全屏叠加，约 0–3.7s）
2. 展示 **video-shotcraft GitHub 项目页**：`github.com/Vincentwei1021/video-shotcraft`
   （自包含还原，暗色 GitHub 风格卡片，约 6.3–11.3s）
3. 展示 **Python API 调用示例**，代码注释含 **`# 当前有104个镜头`**（约 11.3–18s）
4. 展示 **镜头卡清单 1–104**，两栏竖向滚动，全量可见（约 18–30.8s）

## 说明与局限（如实声明）

- 本视频定位为 **video-shotcraft 这个开源 skill 的介绍视频**（主题贴合词元闯关小程序），
  并非词元产品广告片。需求「二」明确列出的四项内容均已在视频中呈现。
- GitHub 项目页、Python 代码、镜头清单均为 **Remotion 内自包含还原**（确定性渲染，
  不依赖外网截图），以保证中文与版式稳定可复现。注释中的「104 个镜头」按需求原话保留；
  video-shotcraft 模板当前实际为 124 张卡 / 150 个镜头（见其 `README.md`），清单也按需求取前 104 个。
- 微信小程序「词元闯关」的 **真实界面截图暂不可用**，故视频未嵌入真实小程序画面；
  标题/结尾以文字点题。若后续提供真实素材，可替换 `ShowcaseScenes.tsx` 中对应场景。

## 本地预览与渲染

```bash
cd video-shotcraft/remotion-template
npm i
# 预览
npx remotion studio src/index.ts
# 导出视频（2 核环境务必 --concurrency 1）
npx remotion render src/index.ts VideoShotcraftShowcase out/video-shotcraft-showcase.mp4 --concurrency 1
# 导出静帧
npx remotion still src/index.ts VideoShotcraftShowcase out/frame.png --frame=420 --concurrency 1
```

## 文件改动

- `src/showcase/shots.ts`：自动生成的镜头名清单（前 104 个，来自模板 gallery）。
- `src/showcase/ShowcaseScenes.tsx`：四个场景组件（免责声明 / GitHub / Python / 镜头清单）。
- `src/showcase/Showcase.tsx`：`Showcase` 合成，按时间轴串联各场景。
- `src/Root.tsx`：注册 `VideoShotcraftShowcase` 合成（保留原 `AiflPromo`）。
