import { AbsoluteFill, Sequence, interpolate, useCurrentFrame } from 'remotion';
import { VisualThemeProvider } from '../themes/visual-theme';
import { SceneDisclaimer, SceneGitHub, ScenePython, SceneShotList } from './ShowcaseScenes';

// Total length: ~36.2s @ 30fps, mirroring the Ink Press template pace.
export const SHOWCASE_TOTAL = 1085;

const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 14, 60, 80], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, 14], [24, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg,#0b1220,#11151f)', justifyContent: 'center', alignItems: 'center', opacity: op }}>
      <div style={{ textAlign: 'center', transform: `translateY(${y}px)` }}>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 16, letterSpacing: '0.34em', color: '#ffd27f', textTransform: 'uppercase', marginBottom: 22 }}>
          WeChat Mini-Program · 词元闯关
        </div>
        <div style={{ fontFamily: '"Segoe UI", "Microsoft YaHei", sans-serif', fontSize: 64, fontWeight: 800, color: '#fdfdfd', lineHeight: 1.3 }}>
          用 video-shotcraft<br />做电影感宣传视频
        </div>
        <div style={{ fontFamily: '"Segoe UI","Microsoft YaHei",sans-serif', fontSize: 24, color: 'rgba(255,255,255,0.6)', marginTop: 26 }}>
          Remotion 导演流程 · 104 个镜头卡 · 全可编辑
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Closer: React.FC = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 16, 120, 145], [0, 1, 1, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg,#0b1220,#1a1320)', justifyContent: 'center', alignItems: 'center', opacity: op }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 20, letterSpacing: '0.2em', color: '#ffd27f', marginBottom: 18 }}>
          github.com/Vincentwei1021/video-shotcraft
        </div>
        <div style={{ fontFamily: '"Segoe UI","Microsoft YaHei",sans-serif', fontSize: 52, fontWeight: 800, color: '#fdfdfd' }}>
          词元闯关 · AI 背单词闯关
        </div>
        <div style={{ fontFamily: '"Segoe UI","Microsoft YaHei",sans-serif', fontSize: 22, color: 'rgba(255,255,255,0.6)', marginTop: 18 }}>
          微信小程序 · 让每个词都串起你的真实语境
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Showcase: React.FC<{ theme?: string }> = ({ theme = 'ink-press' }) => {
  return (
    <VisualThemeProvider theme={theme}>
      <AbsoluteFill>
        <Sequence from={0} durationInFrames={110}>
          <SceneDisclaimer />
        </Sequence>
        <Sequence from={110} durationInFrames={80}>
          <TitleCard />
        </Sequence>
        <Sequence from={190} durationInFrames={150}>
          <SceneGitHub />
        </Sequence>
        <Sequence from={340} durationInFrames={200}>
          <ScenePython />
        </Sequence>
        <Sequence from={540} durationInFrames={385}>
          <SceneShotList />
        </Sequence>
        <Sequence from={925} durationInFrames={160}>
          <Closer />
        </Sequence>
      </AbsoluteFill>
    </VisualThemeProvider>
  );
};
