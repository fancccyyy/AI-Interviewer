import React from 'react';
import './FloatingPanel.css';

function FloatingPanel({ url, onClose }) {
  return (
    <div className="floating-panel">
      <button className="close-btn" onClick={onClose}>X</button>
      <iframe
        src={url}
        title="External Content"
        style={{ width: '100%', height: '90%', border: 'none' }}
      />
    </div>
  );
}

export default FloatingPanel;