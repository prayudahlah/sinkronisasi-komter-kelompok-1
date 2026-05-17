function formatTime(ts) {
  if (ts == null) return '-'
  const d = new Date(ts * 1000)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  const ss = String(d.getSeconds()).padStart(2, '0')
  const ms = String(Math.floor((ts % 1) * 1000)).padStart(3, '0')
  return `${hh}:${mm}:${ss}.${ms}`
}

function steps(entries, avg) {
  const names = entries.map(([name]) => name === 'Master' ? 'Master' : name)
  const vals = entries.map(([, t]) => t)

  const lines = []

  // Avg = (M + S1 + S2) / 3
  lines.push(`Avg = (${names.join(' + ')}) / ${names.length}`)

  // Avg = (1779011541.9385 + ...) / 3
  lines.push(`Avg = (${vals.map(v => v.toFixed(4)).join(' + ')}) / ${names.length}`)

  // Avg = sum / 3
  const sum = vals.reduce((a, b) => a + b, 0)
  lines.push(`Avg = ${sum.toFixed(4)} / ${names.length}`)

  // Avg = result
  lines.push(`Avg = ${avg.toFixed(4)}`)

  return lines
}

function stepAdjustments(entries, avg) {
  return entries
    .filter(([, t]) => t != null)
    .map(([name, t]) => {
      const label = name === 'Master' ? 'Master' : name
      const adj = avg - t
      return `Adjustment(${label}) = ${avg.toFixed(4)} - ${t.toFixed(4)} = ${adj >= 0 ? '+' : ''}${adj.toFixed(4)}`
    })
}

export default function CalculationDetail({ state }) {
  const calc = state?.calculation
  if (!calc || !calc.time_values) return null

  const { iteration, n, avg, time_values, adjustments } = calc

  const entries = Object.entries(time_values).filter(([, t]) => t != null)
  const calcSteps = steps(entries, avg)
  const adjSteps = stepAdjustments(entries, avg)

  return (
    <div className="card">
      <h3>Detail Perhitungan — Iterasi #{iteration}</h3>

      <div className="calc-formula">
        <code>Avg = (T₁ + T₂ + ... + T<sub>n</sub>) / n</code>
        <br />
        <code>Adjustment(i) = Avg − T<sub>i</sub></code>
      </div>

      <div className="calc-steps">
        <div className="calc-steps-title">Langkah Perhitungan:</div>
        {calcSteps.map((line, i) => (
          <div key={i} className="calc-step mono">{line}</div>
        ))}
        <div className="calc-steps-divider" />
        {adjSteps.map((line, i) => (
          <div key={i} className="calc-step mono">{line}</div>
        ))}
      </div>

      <div className="calc-info">
        Jumlah node: <strong>{n}</strong>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Node</th>
              <th>Waktu</th>
              <th>Penyesuaian</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(time_values).map(([name, t]) => (
              <tr key={name}>
                <td className="node-name">{name === 'Master' ? 'Master' : name}</td>
                <td className="mono">{t != null ? formatTime(t) : '-'}</td>
                <td className="mono">
                  {t != null ? (
                    <span className={adjustments[name] >= 0 ? 'adj-pos' : 'adj-neg'}>
                      {adjustments[name] >= 0 ? '+' : ''}{adjustments[name].toFixed(4)}
                    </span>
                  ) : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="calc-result">
        Rata-rata: <strong className="mono">{formatTime(avg)}</strong>
      </div>
    </div>
  )
}
