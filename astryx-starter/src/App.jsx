import {useState} from 'react';
import {
  Badge,
  Banner,
  Button,
  Card,
  Divider,
  Heading,
  Stack,
  Text,
  TextInput,
} from '@astryxdesign/core';

/**
 * Minimal page that proves the integration: components come from
 * @astryxdesign/core, layout/spacing comes from component props, colors come
 * from the theme. It follows the Astryx rules (no raw <div>, no hardcoded
 * hex/px), so it doubles as a reference for agents building UI in this repo.
 */
export default function App() {
  const [name, setName] = useState('');

  return (
    <Stack as="main" padding={8} gap={6} width="100%" maxWidth={880} style={{margin: '0 auto'}}>
      <Stack gap={2}>
        <Heading level={1}>Astryx 已接入</Heading>
        <Text type="supporting">
          这是接入 Astryx 设计系统后的最小可运行示例：组件、主题样式与构建流程均已验证。
        </Text>
      </Stack>

      <Banner
        status="success"
        title="接入验证通过"
        description="组件按 Astryx 规范渲染，主题 CSS 生效，无自定义样式库。"
      />

      <Card padding={6} elevation="low">
        <Stack gap={4}>
          <Stack direction="horizontal" gap={3} align="center" wrap="wrap">
            <Heading level={3}>组件示例</Heading>
            <Badge variant="success" label="Beta" />
          </Stack>

          <Text type="supporting">
            Button、Badge、TextInput、Banner、Card、Heading、Stack、Divider 均为 Astryx 预置组件，
            通过 CLI 的组件索引即可查到用法。
          </Text>

          <Stack direction="horizontal" gap={3} wrap="wrap">
            <Button
              label="主要操作"
              variant="primary"
              onClick={() => setName('已点击主要操作')}
            />
            <Button label="次要操作" variant="secondary" />
            <Button label="幽灵按钮" variant="ghost" />
          </Stack>

          <Divider />

          <TextInput
            label="示例输入"
            placeholder="输入内容，颜色与间距来自主题 token"
            value={name}
            onChange={setName}
          />
          <Text type="supporting">当前值：{name || '（空）'}</Text>
        </Stack>
      </Card>

      <Text type="code">{'astryx search button  ·  astryx component Button  ·  astryx docs tokens'}</Text>
    </Stack>
  );
}
