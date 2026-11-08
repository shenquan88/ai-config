// Showcase scenes for the video-shotcraft intro video.
// Self-contained, deterministic (no Date/Math.random), themed via VisualTheme.
// IMPORTANT: these components are placed inside <Sequence>, so useCurrentFrame()
// is already sequence-relative (0 at the sequence start). Do NOT subtract an
// `enter` offset again — that pushes the local timeline negative and hides content.
import { AbsoluteFill, interpolate, useCurrentFrame } from 'remotion';
import { useVisualTheme, rgba } from '../themes/visual-theme';

const MONO = '"JetBrains Mono", "Fira Code", "SF Mono", Consolas, monospace';
const SANS = '"Segoe UI Variable", "Segoe UI", "Microsoft YaHei", Arial, sans-serif';

// 1) Opening disclaimer — full-screen legal overlay (per ticket 二/1)
export const SceneDisclaimer: React.FC = () => {
  const frame = useCurrentFrame();
  const fade = interpolate(frame, [0, 12, 95, 110], [0, 1, 1, 0]);
  const y = interpolate(frame, [0, 12], [18, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{
        background: 'linear-gradient(160deg,#0b1220 0%,#11151f 60%,#1a1320 100%)',
        justifyContent: 'center',
        alignItems: 'center',
        opacity: fade,
      }}
    >
      <div style={{ textAlign: 'center', transform: `translateY(${y}px)`, padding: '0 120px' }}>
        <div
          style={{
            fontFamily: MONO, fontSize: 15, letterSpacing: '0.32em', color: rgba('#ffd27f', 0.9),
            textTransform: 'uppercase', marginBottom: 26,
          }}
        >
          免责声明 / Disclaimer
        </div>
        <div
          style={{
            fontFamily: SANS, fontSize: 46, fontWeight: 700, lineHeight: 1.5, color: '#fdfdfd',
            maxWidth: 1500,
          }}
        >
          本视频仅供学习交流，请勿用于非法用途
        </div>
        <div
          style={{
            fontFamily: SANS, fontSize: 22, color: rgba('#ffffff', 0.62), marginTop: 22,
            letterSpacing: '0.04em',
          }}
        >
          For learning and communication only — do not use for any unlawful purpose.
        </div>
      </div>
    </AbsoluteFill>
  );
};

// helper: a faux browser chrome frame
const BrowserChrome: React.FC<{ url: string; dark?: boolean }> = ({ url, dark }) => {
  const bar = dark ? '#1b2030' : '#e7ecf3';
  return (
    <div style={{ background: bar, borderRadius: 14, padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 14 }}>
      <div style={{ display: 'flex', gap: 8 }}>
        <span style={{ width: 12, height: 12, borderRadius: 999, background: '#ff5f57' }} />
        <span style={{ width: 12, height: 12, borderRadius: 999, background: '#febc2e' }} />
        <span style={{ width: 12, height: 12, borderRadius: 999, background: '#28c840' }} />
      </div>
      <div style={{ flex: 1, background: dark ? '#0e1320' : '#fff', borderRadius: 8, padding: '8px 16px', fontFamily: MONO, fontSize: 18, color: dark ? '#cdd6e6' : '#33415c' }}>
        {url}
      </div>
    </div>
  );
};

// 2) GitHub repo page (faux, faithful to github.com/Vincentwei1021/video-shotcraft)
export const SceneGitHub: React.FC = () => {
  const frame = useCurrentFrame();
  const show = interpolate(frame, [0, 16], [0, 1], { extrapolateRight: 'clamp' });
  const slide = interpolate(frame, [0, 16], [40, 0], { extrapolateRight: 'clamp' });

  const repoCard: React.CSSProperties = {
    background: '#0d1117', color: '#e6edf3', borderRadius: 16, overflow: 'hidden',
    boxShadow: '0 40px 120px rgba(0,0,0,0.55)', transform: `translateY(${slide}px)`, opacity: show,
    width: 1080, border: '1px solid #21262d',
  };
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg,#0b1220,#11151f)', justifyContent: 'center', alignItems: 'center' }}>
      <div style={repoCard}>
        <BrowserChrome url="github.com/Vincentwei1021/video-shotcraft" dark />
        <div style={{ padding: '26px 30px 30px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontFamily: MONO, fontSize: 22, color: '#58a6ff' }}>
            <span style={{ color: '#8b949e' }}>Vincentwei1021</span>
            <span style={{ color: '#8b949e' }}>/</span>
            <span style={{ color: '#e6edf3', fontWeight: 700 }}>video-shotcraft</span>
            <span style={{ border: '1px solid #30363d', borderRadius: 999, padding: '2px 10px', fontSize: 14, color: '#8b949e' }}>Public</span>
          </div>
          <div style={{ fontFamily: SANS, fontSize: 19, color: '#adbac7', marginTop: 16, lineHeight: 1.6 }}>
            用 Remotion 按导演流程批量制作电影感产品视频的开源 skill。<br />
            Cinematic product promo videos from your own pages, with Remotion.
          </div>
          <div style={{ display: 'flex', gap: 26, marginTop: 22, fontFamily: MONO, fontSize: 17, color: '#adbac7' }}>
            <span>★ 1.2k</span>
            <span>⑂ 138</span>
            <span>● MIT</span>
            <span style={{ color: '#58a6ff' }}>104 镜头卡</span>
          </div>
          <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
            <span style={{ background: '#238636', color: '#fff', borderRadius: 8, padding: '10px 20px', fontFamily: SANS, fontSize: 17, fontWeight: 600 }}>Code ▾</span>
            <span style={{ background: '#21262d', color: '#e6edf3', borderRadius: 8, padding: '10px 20px', fontFamily: SANS, fontSize: 17 }}>★ Star</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// 3) Python API call example (per ticket 二/3) — faithful to the skill's render CLI
export const ScenePython: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame;
  const reveal = interpolate(t, [0, 22], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const lines: { text: string; kind: 'kw' | 'str' | 'com' | 'txt' }[] = [
    { text: '# 用 video-shotcraft 渲染产品宣传片', kind: 'com' },
    { text: 'import os', kind: 'kw' },
    { text: 'from remotion import render', kind: 'kw' },
    { text: '', kind: 'txt' },
    { text: 'shotcraft = VideoShotcraft.from_repo(', kind: 'txt' },
    { text: '    "github.com/Vincentwei1021/video-shotcraft",', kind: 'str' },
    { text: ')', kind: 'txt' },
    { text: '', kind: 'txt' },
    { text: '# 当前有104个镜头  ·  pick the shots you need', kind: 'com' },
    { text: 'shotcraft.render(', kind: 'txt' },
    { text: '    template="Ink Press",', kind: 'str' },
    { text: '    shots=["text-as-mask", "flying-words", "card-stack"],', kind: 'str' },
    { text: '    out="ciyuan-chuangguan.mp4",', kind: 'str' },
    { text: ')', kind: 'txt' },
  ];
  const color = (k: string) =>
    k === 'kw' ? '#ff7b72' : k === 'str' ? '#a5d6ff' : k === 'com' ? '#8b949e' : '#e6edf3';

  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg,#0b1220,#0d1626)', justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ width: 1180, opacity: reveal }}>
        <div style={{ fontFamily: MONO, fontSize: 18, color: '#58a6ff', marginBottom: 14, letterSpacing: '0.08em' }}>
          ▶ render_with_video_shotcraft.py
        </div>
        <div style={{ background: '#0d1117', border: '1px solid #21262d', borderRadius: 14, padding: '26px 30px', fontFamily: MONO, fontSize: 23, lineHeight: 1.85, boxShadow: '0 40px 120px rgba(0,0,0,0.5)' }}>
          {lines.map((l, i) => (
            <div key={i} style={{ color: color(l.kind), whiteSpace: 'pre', opacity: interpolate(t, [i * 1.4, i * 1.4 + 8], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }) }}>
              {l.text || ' '}
            </div>
          ))}
          <div style={{ height: 24, width: 10, background: '#58a6ff', opacity: interpolate(t, [40, 48], [0, 1], { extrapolateRight: 'clamp' }), marginTop: -4 }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

// 4) Shot list 1..104 — two columns that scroll up through all shots (per ticket 二/4)
export const SceneShotList: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame;
  const names = SHOT_NAMES();
  const rowsPerCol = 52; // 2 columns × 52 = 104
  const visibleRows = 13;
  const rowH = 36;
  const windowH = visibleRows * rowH;
  const contentH = rowsPerCol * rowH;
  const maxScroll = Math.max(0, contentH - windowH);
  const scroll = interpolate(t, [30, 355], [0, maxScroll], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const alpha = interpolate(t, [0, 14], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const cols = [names.slice(0, rowsPerCol), names.slice(rowsPerCol, rowsPerCol * 2)];
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(160deg,#0b1220,#0f1422)', justifyContent: 'center', alignItems: 'center', opacity: alpha }}>
      <div style={{ width: 1500, textAlign: 'center' }}>
        <div style={{ fontFamily: MONO, fontSize: 18, letterSpacing: '0.3em', color: '#ffd27f', textTransform: 'uppercase', marginBottom: 10 }}>
          shot library
        </div>
        <div style={{ fontFamily: SANS, fontSize: 34, fontWeight: 700, color: '#fdfdfd', marginBottom: 22 }}>
          镜头卡清单 · 1 – 104
        </div>
        <div
          style={{
            position: 'relative', width: 1200, height: windowH, margin: '0 auto', overflow: 'hidden',
            WebkitMaskImage: 'linear-gradient(180deg, transparent, #000 10%, #000 90%, transparent)',
            maskImage: 'linear-gradient(180deg, transparent, #000 10%, #000 90%, transparent)',
          }}
        >
          {cols.map((col, ci) => (
            <div key={ci} style={{ position: 'absolute', top: 0, left: ci === 0 ? 0 : 620, width: 560, transform: `translateY(${-scroll}px)` }}>
              {col.map((n, i) => {
                const idx = ci * rowsPerCol + i + 1;
                return (
                  <div key={i} style={{ height: rowH, display: 'flex', gap: 12, alignItems: 'center', fontFamily: MONO, fontSize: 18, color: '#cdd6e6', textAlign: 'left' }}>
                    <span style={{ color: '#58a6ff', minWidth: 34, textAlign: 'right' }}>{idx}</span>
                    <span>{n}</span>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// lazy import to avoid circular at module top
import { SHOT_NAMES_104 } from './shots';
const SHOT_NAMES = () => SHOT_NAMES_104;
