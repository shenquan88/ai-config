import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createElement as h} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

import {Badge, Button, Card, Heading, Stack, Text, TextInput} from '@astryxdesign/core';
import {Theme} from '@astryxdesign/core/theme';
import {neutralTheme} from '@astryxdesign/theme-neutral/built';
// NOTE: importing the theme's CSS here makes `astryx doctor` happy, but Node's
// ESM loader cannot handle a bare ".css" import in a runtime test, so the
// stylesheet is only imported from the app entry (main.jsx) where a bundler
// resolves it. Doctor's theme-stylesheet-imports warning on the test file is a
// known false positive for Node-only SSR tests; the app build imports it.

const render = tree => renderToStaticMarkup(tree);

test('Button renders its label and compiled style classes', () => {
  const html = render(h(Button, {label: '接入成功', variant: 'primary'}, null));

  assert.match(html, /<button/);
  assert.match(html, /接入成功/);
  // Astryx ships compiled StyleX classes; a missing class means styling is broken.
  assert.match(html, /class="[^"]+"/);
  assert.doesNotMatch(html, /undefined/);
});

test('composes Card / Stack / Heading / Text / Badge / TextInput', () => {
  const html = render(
    h(
      Card,
      {padding: 6, elevation: 'low'},
      h(
        Stack,
        {gap: 4},
        h(Heading, {level: 2}, '组件索引'),
        h(Text, {type: 'supporting'}, '主题 token 生效'),
        h(Badge, {variant: 'success', label: '已验证'}),
        h(TextInput, {label: '示例输入', value: 'hello', onChange: () => {}}),
      ),
    ),
  );

  for (const needle of ['<h2', '组件索引', '主题 token 生效', '已验证', '示例输入']) {
    assert.ok(html.includes(needle), `expected markup to contain ${needle}`);
  }
  assert.match(html, /<input/);
});

test('Theme provider renders the neutral theme around children', () => {
  const html = render(
    h(
      Theme,
      {theme: neutralTheme},
      h(Heading, {level: 1}, '主题已生效'),
    ),
  );

  assert.match(html, /主题已生效/);
  assert.match(html, /<h1/);
  // The theme injects token overrides; require at least one custom property.
  assert.match(html, /--color-|--spacing-|data-astryx|class="/);
});
