import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';

const TypingContainer = styled.span`
  display: inline-block;
  position: relative;
  &::after {
    content: '|';
    display: inline-block;
    animation: blink-caret 0.75s step-end infinite;
    margin-left: 2px;
    vertical-align: baseline;
  }
`;

const TypingEffect = ({ text }) => {
  return (
    <TypingContainer>
      <span><ReactMarkdown>{text}</ReactMarkdown></span>
    </TypingContainer>
  );
};

export default TypingEffect;