import Header from './components/Header.jsx'
import SlaveTable from './components/SlaveTable.jsx'
import TimeChart from './components/TimeChart.jsx'
import CalculationDetail from './components/CalculationDetail.jsx'
import useWebSocket from './useWebSocket.js'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`

export default function App() {
  const { state, connected, send } = useWebSocket(WS_URL)

  const handleStartStop = () => {
    send({ action: state?.running ? 'stop' : 'start' })
  }

  return (
    <div className="app">
      <Header state={state} connected={connected} onStartStop={handleStartStop} />
      <main className="main">
        <div className="grid">
          <SlaveTable state={state} />
          <TimeChart state={state} />
        </div>
        <CalculationDetail state={state} />
      </main>
    </div>
  )
}
