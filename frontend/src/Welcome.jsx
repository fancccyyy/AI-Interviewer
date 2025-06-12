import { useState } from 'react'
import './Welcome.css'
import { Button, ConfigProvider, Space } from 'antd'
import { createStyles } from 'antd-style';

const useStyle = createStyles(({ prefixCls, css }) => ({
  linearGradientButton: css`
    &.${prefixCls}-btn-primary:not([disabled]):not(.${prefixCls}-btn-dangerous) {
      > span {
        position: relative;
      }

      &::before {
        content: '';
        background: linear-gradient(135deg, #6253e1, #04befe);
        position: absolute;
        inset: -1px;
        opacity: 1;
        transition: all 0.3s;
        border-radius: inherit;
      }

      &:hover::before {
        opacity: 0;
      }
    }
  `,
}));

function Welcome({ startInterview }) {
  const { styles } = useStyle();

  return (
    <div>
      <Space direction="vertical" size={"large"} style={{ display: 'flex', padding: '20px'}}>
        <div>
          <h1 style={{ color: '#060606' }}>你好👋，<br class="mobile-break" />我是Kora的语音面试官</h1>
          <h2 style={{ color: '#020202' }}>接下来我会用中文向你提问一些常见面试问题，请用语音作答。</h2>
          
        </div>
        <ConfigProvider
          button={{
            className: styles.linearGradientButton,
          }}
        >
          <Space>
            <Button onClick={startInterview} type="primary" size="large">
            让我们开始吧 👉
            </Button>
          </Space>
        </ConfigProvider>
      </Space>
    </div>
  )
}

export default Welcome
