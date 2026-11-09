import { useEffect, useState, useCallback, useRef } from 'react'
import { useToast } from '@chakra-ui/react'

interface WebSocketMessage {
  type: string
  data: any
  timestamp: number
}

export function useWebSocket(url: string) {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const ws = useRef<WebSocket | null>(null)
  const toast = useToast()

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url)

      ws.current.onopen = () => {
        setIsConnected(true)
        toast({
          title: 'Connected',
          description: 'Real-time feed connected',
          status: 'success',
          duration: 2000,
        })
      }

      ws.current.onclose = () => {
        setIsConnected(false)
        toast({
          title: 'Disconnected',
          description: 'Attempting to reconnect...',
          status: 'warning',
          duration: 2000,
        })
        // Reconnect after 3 seconds
        setTimeout(connect, 3000)
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setMessages(prev => [...prev, message].slice(-100)) // Keep last 100
        } catch (error) {
          console.error('WebSocket message parse error:', error)
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('WebSocket connection error:', error)
    }
  }, [url, toast])

  useEffect(() => {
    connect()
    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [connect])

  const send = useCallback((data: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  return { isConnected, messages, send, clearMessages }
}