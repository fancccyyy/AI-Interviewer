import React, { useState, useRef, useEffect } from 'react';
import { Input, Button } from 'antd';
import { AudioOutlined, SendOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const InputWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`;

const SpeechButton = styled(Button)`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const UserInput = ({ onSendMessage }) => {
  const [text, setText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [interimText, setInterimText] = useState('');
  
  const mediaStreamRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const wsRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // 清理函数，在组件卸载时关闭所有连接和资源
    return () => {
      stopListening();
    };
  }, []);

  const startListening = async () => {
    if (isListening) return;

    try {
      mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsListening(true);
      setInterimText(''); // 清空之前的临时文本

      audioContextRef.current = new window.AudioContext({ sampleRate: 16000 });
      const source = audioContextRef.current.createMediaStreamSource(mediaStreamRef.current);

      const bufferSize = 4096;
      const channels = 1;
      processorRef.current = audioContextRef.current.createScriptProcessor(bufferSize, channels, channels);
      source.connect(processorRef.current);
      processorRef.current.connect(audioContextRef.current.destination);

      const uuid = crypto.randomUUID();
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/asr/${uuid}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket 连接成功');
      };

      wsRef.current.onmessage = (event) => {
        const result = JSON.parse(event.data);
        if (result.text) {
          if (result.is_end) {
            setText(prevText => prevText + result.text); // 将最终结果追加到已有文本
            setInterimText(''); // 清空临时文本
          } else {
            setInterimText(result.text); // 显示中间结果
          }
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        stopListening(); // 发生错误时停止监听
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket 连接关闭');
        if (isListening) { // 避免在手动停止后再次调用 stopListening
          stopListening();
        }
      };

      processorRef.current.onaudioprocess = (e) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          const inputBuffer = e.inputBuffer;
          const inputData = inputBuffer.getChannelData(0);
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32767));
          }
          wsRef.current.send(pcmData.buffer);
        }
      };

    } catch (error) {
      console.error('启动语音识别失败:', error);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (!isListening && !mediaStreamRef.current && !audioContextRef.current && !processorRef.current && !wsRef.current) return;

    setIsListening(false);

    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current.onaudioprocess = null; // 移除事件处理器
      processorRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close().catch(e => console.error("Error closing AudioContext: ", e));
      audioContextRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }

    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN) {
        // 可以选择发送一个结束信号给后端
        // wsRef.current.send(JSON.stringify({ end_of_speech: true }));
      }
      wsRef.current.close();
      wsRef.current = null;
    }
    console.log('语音识别已停止');
  };

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleSendMessage = () => {
    if (text.trim() || interimText.trim()) { // 允许发送正在识别的临时文本
      const messageToSend = text.trim() || interimText.trim();
      console.log(`发送文本: ${messageToSend}`);
      onSendMessage(messageToSend);
      setText('');
      setInterimText('');
      // 如果正在监听，发送消息后可以选择停止监听或继续
      if (isListening) stopListening(); 
    }
  };

  return (
    <InputWrapper>
      <SpeechButton
        type={isListening ? 'danger' : 'primary'}
        icon={<AudioOutlined />}
        onClick={isListening ? stopListening : startListening}
        style={{ height: '57px' }}
      >
        {isListening ? '停止' : '语音'}
      </SpeechButton>
      <Input.TextArea
        ref={inputRef}
        placeholder="请输入或使用语音识别"
        value={text + interimText} // 合并显示最终文本和临时文本
        onChange={handleTextChange}
        onPressEnter={(e) => {
          e.preventDefault(); // 阻止默认的换行行为
          handleSendMessage();
        }}
        autoSize={{ minRows: 2, maxRows: 40 }} // 设置最小和最大行数，允许自动增长
        style={{ resize: 'none', fontSize: '16px'}} // 禁用手动调整大小
      />
      <Button
        type="primary"
        icon={<SendOutlined />}
        onClick={handleSendMessage}
        disabled={!text.trim() && !interimText.trim()} // 允许在有临时文本时提交
        style={{ height: '57px' }}
      >
        提交
      </Button>
    </InputWrapper>
  );
};

export default UserInput;