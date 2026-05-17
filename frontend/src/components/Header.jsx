export default function Header({ state, connected, onStartStop }) {
  if (!state) return null

  return (
    <header className="header">
      <div className="header-left">
        <h1>Algoritma Berkeley</h1>
        <span className="subtitle">Dashboard Sinkronisasi Jam</span>
      </div>
      <div className="header-center">
        <span className={`badge ${connected ? 'badge-ok' : 'badge-err'}`}>
          {connected ? 'Terhubung' : 'Terputus'}
        </span>
        <span className={`badge ${state.running ? 'badge-ok' : 'badge-warn'}`}>
          {state.running ? 'Berjalan' : 'Berhenti'}
        </span>
        <span className="info-text">
          Iterasi: <strong>{state.iteration}</strong> &nbsp;|&nbsp; Interval: <strong>{state.interval}s</strong>
        </span>
      </div>
      <div className="header-right">
        <button className="btn" onClick={onStartStop}>
          {state.running ? 'Berhenti' : 'Mulai'}
        </button>
      </div>
    </header>
  )
}
