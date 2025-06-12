import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { Avatar } from 'antd';
import TypingEffect from './TypingEffect';

const MessageContainer = styled.div`
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
`;

// const Avatar = styled.div`
//   width: 32px;
//   height: 32px;
//   border-radius: 50%;
//   background-color: #1890ff;
//   color: white;
//   display: flex;
//   justify-content: center;
//   align-items: center;
//   margin-right: 12px;
//   font-weight: bold;
// `;

const Content = styled.div`
  background-color: ${props => (props.is_ai ? '#f0f2f5' : '#e6f7ff')};
  color: ${props => (props.is_ai ? 'rgba(0, 0, 0, 0.85)' : 'rgba(0, 0, 0, 0.65)')};
  border-radius: 4px;
  padding: ${props => (props.is_ai ? '1px 16px' : '12px 16px')};
  line-height: 1.5;
  word-break: break-word;
  max-width: 70%;
`;

const CandidateMessageContainer = styled(MessageContainer)`
  flex-direction: row-reverse;
`;

const Message = ({ sender, content, isComplete }) => {
  const is_ai = sender === 'ai' || sender === 'system';
  // 自定义渲染函数实现a标签新窗口打开
  const renderers = {
    a: ({ node, ...props }) => (
      <a {...props} target="_blank" rel="noopener noreferrer" />
    ),
  };

  return is_ai ? (
    <MessageContainer>
      <Avatar style={{background: "linear-gradient(to right, rgb(185, 43, 39), rgb(21, 101, 192))", marginRight: '16px'}}><b>AI</b></Avatar>
      <Content is_ai={is_ai}>
        {/* {isComplete ?  : <TypingEffect text={content} />} */}
        {/* {<ReactMarkdown>{content}</ReactMarkdown>} */}
        {content === "" ? (
          <ReactMarkdown>加载中...</ReactMarkdown>
        ) : (
          sender === 'system' ? (
            <ReactMarkdown components={renderers}>{'系统提示：' + content}</ReactMarkdown>
          ) : (
            <ReactMarkdown components={renderers}>{content}</ReactMarkdown>
          )
        )}
      </Content>
    </MessageContainer>
  ) : (
    <CandidateMessageContainer>
      <Avatar style={{background: "linear-gradient(to right, rgb(0, 180, 219), rgb(0, 131, 176))", marginLeft: '16px'}}><b>你</b></Avatar>
      <Content is_ai={is_ai}>{content}</Content>
    </CandidateMessageContainer>
  );
};

export default Message;