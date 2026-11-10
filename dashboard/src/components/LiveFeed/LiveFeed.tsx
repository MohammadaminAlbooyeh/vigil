import { useEffect, useRef } from 'react'
import { Box, Badge, Text } from '@chakra-ui/react'
import { useWebSocket } from '../../hooks/useWebSocket'

interface LiveFeedProps {
  cameraId?: string
}

export function LiveFeed({ cameraId }: LiveFeedProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const { messages, isConnected } = useWebSocket(
    `ws://localhost:8000/ws/live${cameraId ? `?camera=${cameraId}` : ''}`
  )

  useEffect(() => {
    if (messages.length > 0) {
      const latest = messages[messages.length - 1]
      if (latest.type === 'detection' && canvasRef.current) {
        drawDetection(latest.data)
      }
    }
  }, [messages])

  const drawDetection = (data: any) => {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
    // Draw bounding boxes
    data.detections?.forEach((d: any) => {
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 2
      ctx.strokeRect(d.bbox[0], d.bbox[1], d.bbox[2], d.bbox[3])
      ctx.fillStyle = '#00ff00'
      ctx.fillText(`${d.class} ${(d.confidence * 100).toFixed(0)}%`, d.bbox[0], d.bbox[1] - 5)
    })
  }

  return (
    <Box border="1px solid gray" borderRadius="md" p={2}>
      <canvas
        ref={canvasRef}
        width={640}
        height={480}
        style={{ width: '100%', height: 'auto' }}
      />
      <Box mt={2}>
        <Badge colorScheme={isConnected ? 'green' : 'red'}>
          {isConnected ? 'LIVE' : 'OFFLINE'}
        </Badge>
        <Text ml={2} display="inline">
          Camera: {cameraId || 'All'}
        </Text>
      </Box>
    </Box>
  )
}