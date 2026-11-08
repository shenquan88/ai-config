import { Composition } from 'remotion';
import { AIFL_TOTAL } from './aifl/Main';
import { ThemedFilm } from './themes/ThemedFilm';
import { Showcase, SHOWCASE_TOTAL } from './showcase/Showcase';

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="AiflPromo"
        component={ThemedFilm}
        defaultProps={{ theme: 'ink-press' }}
        durationInFrames={AIFL_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
      <Composition
        id="VideoShotcraftShowcase"
        component={Showcase}
        defaultProps={{ theme: 'ink-press' }}
        durationInFrames={SHOWCASE_TOTAL}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
