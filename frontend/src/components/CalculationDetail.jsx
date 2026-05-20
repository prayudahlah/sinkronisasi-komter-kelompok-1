function formatTime(ts) {
  if (ts == null) return '-'
  const d = new Date(ts * 1000)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  const ms = String(Math.floor((ts % 1) * 1000)).padStart(3, '0')
  return `${hh}:${mm}:${ss}.${ms}`
}

export default function CalculationDetail({ state }) {
  const calc = state?.calculation
  if (!calc || !calc.offsets) return (
    <div className="card">
      <h3>Detail Perhitungan</h3>
      <p className="muted" style={{ textAlign: 'center', padding: '40px 0' }}>Menunggu iterasi pertama...</p>
    </div>
  )

  const { iteration, n, avg_offset, master_time, universal_time, clock_adjusted, offsets } = calc

  const entries = Object.entries(offsets).filter(([, v]) => v != null)

  const sum = entries.reduce((a, [, v]) => a + v, 0)

  return (
    <div className="card">
      <h3>Detail Perhitungan — Iterasi #{iteration}</h3>

      <div className="calc-formula">
        <code>Offset(i) = T<sub>master</sub> − T<sub>i</sub></code>
        <br />
        <code>Avg_Offset = Σ Offset(i) / n</code>
        <br />
        <code>Universal_Time = T<sub>master</sub> + Avg_Offset</code>
      </div>

      <div className="calc-steps">
        <div className="calc-steps-title">Langkah Perhitungan:</div>

        {/* Per offset */}
        {entries.map(([name, off], i) => (
          <div key={i} className="calc-step mono">
            Offset({name === 'master' ? 'Master' : name}) = {formatTime(master_time)} − T<sub>{name === 'master' ? 'm' : 'i'}</sub> = {off >= 0 ? '+' : ''}{off.toFixed(4)}
          </div>
        ))}

        <div className="calc-steps-divider" />

        {/* Avg Offset */}
        <div className="calc-step mono">
          Avg_Offset = ({entries.map(([, v]) => v.toFixed(4)).join(' + ')}) / {entries.length}
        </div>
        <div className="calc-step mono">
          Avg_Offset = {sum.toFixed(4)} / {entries.length}
        </div>
        <div className="calc-step mono">
          Avg_Offset = {avg_offset.toFixed(4)}
        </div>

        <div className="calc-steps-divider" />

        {/* Universal Time */}
        <div className="calc-step mono">
          Universal_Time = {formatTime(master_time)} + ({avg_offset >= 0 ? '+' : ''}{avg_offset.toFixed(4)})
        </div>
        <div className="calc-step mono highlight">
          Universal_Time = <strong>{formatTime(universal_time)}</strong>
        </div>
      </div>

      <div className="calc-info">
        Jumlah node: <strong>{n}</strong> &nbsp;|&nbsp;
        Clock adjusted: <strong className={clock_adjusted ? 'adj-pos' : 'adj-neg'}>{clock_adjusted ? 'Berhasil' : 'Gagal'}</strong>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Node</th>
              <th>Offset</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="node-name">Master</td>
              <td className="mono adj-pos">+0.0000</td>
            </tr>
            {entries.map(([name, off]) => (
              <tr key={name}>
                <td className="node-name">{name}</td>
                <td className="mono">
                  <span className={off >= 0 ? 'adj-pos' : 'adj-neg'}>
                    {off >= 0 ? '+' : ''}{off.toFixed(4)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="calc-result">
        Universal Time: <strong className="mono">{formatTime(universal_time)}</strong>
      </div>
    </div>
  )
}
