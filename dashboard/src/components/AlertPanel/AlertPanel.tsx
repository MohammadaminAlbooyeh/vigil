import { Box, VStack, Text, Badge, Card, CardBody, HStack, useColorModeValue } from '@chakra-ui/react'
import { Shield, AlertTriangle } from 'lucide-react'

const MOCK_ALERTS = [
  { id: '1', type: 'Motion', device: 'ESP32-CAM-01', severity: 'high', time: '2m ago', status: 'active' },
  { id: '2', type: 'Intrusion', device: 'ESP32-S3-02', severity: 'critical', time: '15m ago', status: 'acknowledged' },
  { id: '3', type: 'Tamper', device: 'ESP32-CAM-03', severity: 'medium', time: '1h ago', status: 'resolved' },
]

const severityColor = (s: string) => {
  switch (s) {
    case 'critical': return 'red'
    case 'high': return 'orange'
    case 'medium': return 'yellow'
    default: return 'blue'
  }
}

export function AlertPanel() {
  const text = useColorModeValue('gray.800', 'gray.100')
  const muted = useColorModeValue('gray.500', 'gray.400')

  return (
    <Box>
      <VStack align="start" spacing={4}>
        <Box as="span" fontSize="2xl" fontWeight="bold" color={text}>Alerts</Box>
        <Text color={muted} fontSize="sm">Real-time security alerts from edge devices.</Text>
        <Card borderRadius="xl" mt={4}>
          <CardBody>
            {MOCK_ALERTS.map((a) => (
              <Box key={a.id} py={3} borderBottom="1px solid" borderColor="gray.100" display="flex" alignItems="center" justifyContent="space-between">
                <HStack align="center" spacing={3} flex={1}>
                  <Box as="span">{a.severity === 'critical' ? <AlertTriangle size={18} color="red.500" /> : <Shield size={18} />}</Box>
                  <Text fontWeight="medium" color={text}>{a.type}</Text>
                  <Text color={muted} fontSize="sm" ml={2}>{a.device}</Text>
                </HStack>
                <HStack align="center" spacing={2}>
                  <Badge colorScheme={severityColor(a.severity)} size="sm">{a.severity}</Badge>
                  <Text color={muted} fontSize="xs">{a.time}</Text>
                  <Badge colorScheme="green" size="sm">{a.status}</Badge>
                </HStack>
              </Box>
            ))}
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}
