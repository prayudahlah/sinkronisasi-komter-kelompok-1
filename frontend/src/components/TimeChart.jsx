import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

export default function TimeChart({ state }) {
  if (!state?.current) return null

  const nodes = Object.entries(state.current)
  const data = nodes
    .filter(([, info]) => info.offset != null)
    .map(([name, info]) => ({
      name: name === 'Master' ? 'Master' : name,
      offset: info.offset,
      time: info.time,
    }))

  if (data.length === 0) return (
    <div className="card">
      <h3>Offset dari Master (Selisih per Node)</h3>
      <p className="muted" style={{ textAlign: 'center', padding: '60px 0' }}>Menunggu data iterasi pertama...</p>
    </div>
  )

  const MIN_RANGE = 0.5
  const maxAbs = Math.max(...data.map(d => Math.abs(d.offset)), MIN_RANGE)
  const yDomain = [-maxAbs * 1.2, maxAbs * 1.2]

  return (
    <div className="card">
      <h3>Offset dari Master (Selisih per Node)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" tick={{ fill: '#6b7280' }} />
          <YAxis domain={yDomain} tick={{ fill: '#6b7280' }} tickFormatter={(v) => v.toFixed(2)} />
          <Tooltip
            contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: 6 }}
            labelStyle={{ color: '#1f2937' }}
            formatter={(val, name) => [val.toFixed(4), name === 'offset' ? 'Offset' : name]}
          />
          <ReferenceLine y={0} stroke="#d1d5db" />
          <Bar dataKey="offset" name="Offset">
            {data.map((entry, idx) => (
              <Cell key={idx} fill={entry.offset >= 0 ? '#22c55e' : '#ef4444'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
