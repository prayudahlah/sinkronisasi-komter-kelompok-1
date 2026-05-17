function formatTime(ts) {
  if (ts == null) return '-'
  const d = new Date(ts * 1000)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  const ms = String(Math.floor((ts % 1) * 1000)).padStart(3, '0')
  return `${hh}:${mm}:${ss}.${ms}`
}

export default function SlaveTable({ state }) {
  if (!state?.current) return null

  const nodes = Object.entries(state.current)

  return (
    <div className="card">
      <h3>Status Node</h3>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Node</th>
              <th>Status</th>
              <th>Waktu</th>
              <th>Penyesuaian</th>
            </tr>
          </thead>
          <tbody>
            {nodes.map(([name, info]) => (
              <tr key={name}>
                <td>
                  <span className="node-name">{name}</span>
                </td>
                <td>
                  <span className={`dot ${info.status === 'online' ? 'dot-on' : 'dot-off'}`} />
                  {info.status}
                </td>
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
    </div>
  )
}
