import { useEffect, useRef, useState, useCallback } from 'react'

export default function useWebSocket(url) {
  const [state, setState] = useState(null)
  const [connected, setConnected] = useState(false)
  const ws = useRef(null)

  useEffect(() => {
    function connect() {
      ws.current = new WebSocket(url)
      ws.current.onopen = () => setConnected(true)
      ws.current.onclose = () => { setConnected(false); setTimeout(connect, 1000) }
      ws.current.onmessage = (e) => setState(JSON.parse(e.data))
      ws.current.onerror = () => {}
    }
    connect()
    return () => ws.current?.close()
  }, [url])

  const send = useCallback((data) => {
    ws.current?.send(JSON.stringify(data))
  }, [])

  return { state, connected, send }
}
