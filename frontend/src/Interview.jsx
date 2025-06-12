import './Interview.css'

import React, { useState, useEffect, useRef, createContext } from 'react';
import styled from 'styled-components';
import { Layout } from 'antd';
import Message from './components/Message';
import UserInput from './components/UserInput';
import PopInput from './components/PopInput';

const { Content, Footer } = Layout;

const ChatContainer = styled(Content)`
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
`;

const StyledFooter = styled(Footer)`
  text-align: center;
  background: #f5f5f5;
  border-radius: 8px;
`;

// 创建 InterviewContext
export const InterviewContext = createContext(null);

function Interview() {
  const [messages, setMessages] = useState([]);
  const chatContainerRef = useRef(null);
  const uid = useRef(crypto.randomUUID());
  const [interviewStyle, setInterviewStyle] = useState({style: '专业'});

  useEffect(() => {
    const controller = new AbortController();

    const fetchFirstMessage = async () => {
      // 乐观UI，先发送占位消息
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', content: '加载中...', isComplete: false }]); // placeholder

      try {
        const response = await fetch(`/ai/start/${uid.current}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let receivedText = '';
        // setMessages(prevMessages => [...prevMessages, { sender: 'ai', content: '加载中', isComplete: false }]); // placeholder
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            break;
          }
          const chunk = decoder.decode(value, { stream: true });
          // console.log('Received chunk at', Date.now(), chunk);
          // chunk格式：data: {"content": "\u8be6\u7ec6\u7684\u8bb2\u8ff0\uff0c\u8ba9\u6211\u4eec", "status": "answering"}
          const parts = chunk.split('\n\n'); // 分割多个 event
          for (const part of parts) {
            if (part.startsWith('data: ')) {
              const chunkStr = part.slice(5); // 去掉 "data: " 前缀
              let chunkObj;
              try {
                chunkObj = JSON.parse(chunkStr);
              } catch (e) {
                console.error('JSON parse error:', e, 'Invalid chunk:', chunkStr);
                continue;
              }

              receivedText += chunkObj.content;

              // 更新消息内容
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                // console.log('newMessage', newMessages);
                // console.log('receiveText', receivedText);
                if (lastMessage.sender === 'ai') {
                  lastMessage.content = receivedText;
                }
                return newMessages;
              });

              // 延时模拟打字机
              await new Promise(resolve => setTimeout(resolve, 100));
            }
          }
        }
        setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage.sender === 'ai') {
              lastMessage.isComplete = true;
            }
            return newMessages;
          });
      } catch (error) {
        console.error('Failed to fetch first message:', error);
      }
    };

    fetchFirstMessage();

    return () => {
      controller.abort();
    };
  }, []);

  useEffect(() => {
    requestAnimationFrame(() => {
      window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: 'smooth'
      });
    });
  }, [messages]);

  const handleSendMessage = async (userMessage) => {
    // 添加用户消息到聊天列表
    setMessages(prevMessages => [...prevMessages, { sender: 'user', content: userMessage, isComplete: true }]);
    try {
      // 发送 POST 请求到 /ai/answer
      const answerResponse = await fetch('/ai/answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ uid: uid.current, answer: userMessage }),
      });

      if (!answerResponse.ok) {
        throw new Error(`Failed to send answer: ${answerResponse.status}`);
      }

      // 获取下一个问题
      setMessages(prevMessages => [...prevMessages, { sender: 'ai', content: '', isComplete: false }]);

      const nextQuestionResponse = await fetch(`/ai/next-question/${uid.current}`);
      if (!nextQuestionResponse.ok) {
        throw new Error(`Failed to fetch next question: ${nextQuestionResponse.status}`);
      }

      const reader = nextQuestionResponse.body.getReader();
      const decoder = new TextDecoder();
      let receivedText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        const chunk = decoder.decode(value, { stream: true });
        const parts = chunk.split('\n\n');
        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const chunkStr = part.slice(5);
            let chunkObj;
            try {
              chunkObj = JSON.parse(chunkStr);
            } catch (e) {
              console.error('JSON parse error:', e, 'Invalid chunk:', chunkStr);
              continue;
            }
            receivedText += chunkObj.content;
            setMessages(prev => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              if (lastMessage.sender === 'ai') {
                lastMessage.content = receivedText;
              }
              return newMessages;
            });

            // 延时模拟打字机
            await new Promise(resolve => setTimeout(resolve, 100));
          }
        }
      }
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage.sender === 'ai') {
          lastMessage.isComplete = true;
        }
        return newMessages;
      });
    } catch (error) {
      console.error('Error during message handling:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage.sender === 'ai') {
          lastMessage.content = '出现错误，可能是网络问题或服务器问题，请稍后重试';
        }
        lastMessage.isComplete = true;
        return newMessages;
      });
    }
  };

  return (
    <InterviewContext.Provider value={{ interviewStyle, setInterviewStyle }}>
      <Layout style={{ minWidth: '100%', minHeight: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'transparent' }}>
          <Content
            ref={chatContainerRef}
            style={{
              padding: '14px',
              flexGrow: 1,
              overflowY: 'auto',
              boxSizing: 'border-box',
              backgroundColor: 'transparent',
              minHeight: 0,
            }}
          >
            {messages.map((msg, index) => (
              <div key={index} style={{ opacity: 1, transform: 'translateY(20px)', animation: 'fadeIn 0.3s ease-out forwards' }}>
                <Message sender={msg.sender} content={msg.content} isComplete={msg.isComplete} />
              </div>
            ))}
          </Content>
        <div style={{ height: '20px', position: 'sticky', bottom: 0 }} />
        <div style={{ height: '20px', position: 'sticky', bottom: 0 }}>
          <PopInput />
        </div>
        <div style={{ height: '20px', position: 'sticky', bottom: 0 }} />
        <StyledFooter style={{ padding: '20px', position: 'sticky', bottom: 0 }}>
          <UserInput onSendMessage={handleSendMessage} />
        </StyledFooter>
        <div style={{ height: '20px', position: 'sticky', bottom: 0 }} />
      </Layout>
    </InterviewContext.Provider>
  );
}

export default Interview;