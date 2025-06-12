import { useState, useRef } from 'react'
import { CSSTransition, SwitchTransition } from 'react-transition-group'
import './App.css'
import Welcome from './Welcome.jsx'
import Interview from './Interview.jsx'

function App() {
  const [currentView, setCurrentView] = useState('welcome')
  const nodeRef = useRef(null)

  const startInterview = () => {
    console.log(currentView)
    setCurrentView('interview')
  }

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      // justifyContent: 'center',
      // alignItems: 'center',
      flex: 1,
      position: 'relative' // 用于定位动画组件
    }}>
      <SwitchTransition>
        <CSSTransition
          key={currentView}
          timeout={300} // 动画持续时间
          classNames="fade" // CSS 类名前缀
          unmountOnExit // 组件离开后卸载
          nodeRef={nodeRef}
        >
          <div style={{
            height: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            flex: 1,
            }} ref={nodeRef}>
            {currentView === 'welcome' ?
              <Welcome startInterview={startInterview} /> : <Interview />
            }
          </div>
        </CSSTransition>
      </SwitchTransition>
    </div>
  )
}

export default App
