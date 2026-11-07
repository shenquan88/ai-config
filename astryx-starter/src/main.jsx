import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {Theme} from '@astryxdesign/core/theme';

// Astryx ships pre-built CSS: no PostCSS, Babel or Vite plugin is needed.
// Order matters: reset -> component styles -> theme token overrides.
// The generated src/astryx-themes.js imports the theme + font stylesheets.
import '@astryxdesign/core/reset.css';
import '@astryxdesign/core/astryx.css';

import {themes, defaultThemeSlug} from './astryx-themes';
import App from './App.jsx';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Theme theme={themes[defaultThemeSlug]}>
      <App />
    </Theme>
  </StrictMode>,
);
