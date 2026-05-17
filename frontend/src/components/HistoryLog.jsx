function formatTime(ts) {
  if (ts == null) return '-'
  const d = new Date(ts * 1000)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  const ms = String(Math.floor((ts % 1) * 1000)).padStart(3, '0')
  return `${hh}:${mm}:${ss}.${ms}`
}

export default function HistoryLog({ state }) {
  const history = state?.history ?? []

  if (history.length === 0) {
    return (
      <div className="card">
        <h3>Riwayat Penyesuaian</h3>
        <p className="muted">Menunggu iterasi pertama...</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h3>Riwayat Penyesuaian</h3>
      <div className="log-container">
        {history.map((entry) => (
          <div key={entry.iteration} className="log-entry">
            <div className="log-header">Iterasi #{entry.iteration}</div>
            <table>
              <thead>
                <tr>
                  <th>Node</th>
                  <th>Waktu</th>
                  <th>Penyesuaian</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(entry.data).map(([name, info]) => (
                  <tr key={name}>
                    <td>{name}</td>
                    <td className="mono">{formatTime(info.time)}</td>
                    <td className="mono">
                      <span className={info.adjustment >= 0 ? 'adj-pos' : 'adj-neg'}>
                        {info.adjustment >= 0 ? '+' : ''}{info.adjustment?.toFixed(4)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </div>
  )
}
