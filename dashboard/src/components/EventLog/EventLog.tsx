import { Box, VStack, Text, Badge, Card, CardBody, HStack, useColorModeValue } from '@chakra-ui/react'
import { Clock, AlertCircle, Info } from 'lucide-react'

const EVENTS = [
  { id: '1', type: 'motion_detected', device: 'ESP32-CAM-01', severity: 'info', time: '10:42:15', meta: 'Person detected' },
  { id: '2', type: 'temperature', device: 'ESP32-S3-01', severity: 'warning', time: '10:40:02', meta: 'Temp 38.2°C' },
  { id: '3', type: 'motion_detected', device: 'ESP32-CAM-02', severity: 'info', time: '10:38:47', meta: 'Motion detected' },
  { id: '4', type: 'door_open', device: 'ESP32-Actuator-01', severity: 'info', time: '10:35:10', meta: 'Door unlocked' },
]

const iconFor = (t: string) => {
  switch (t) {
    case 'motion_detected': return <AlertCircle size={16} color="orange.500" />
    case 'temperature': return <Info size={16} color="blue.500" />
    default: return <Clock size={16} color="gray.400" />
  }
}

export function EventLog() {
  const text = useColorModeValue('gray.800', 'gray.100')
  const muted = useColorModeValue('gray.500', 'gray.400')

  return (
    <Box>
      <VStack align="start" spacing={4}>
        <Box as="span" fontSize="2xl" fontWeight="bold" color={text}>Event Log</Box>
        <Text color={muted} fontSize="sm">Chronological log of system events.</Text>
        <Card borderRadius="xl" mt={4}>
          <CardBody>
            {EVENTS.map((e) => (
              <Box key={e.id} py={3} borderBottom="1px solid" borderColor="gray.100" display="flex" alignItems="center" justifyContent="space-between">
                <HStack align="center" spacing={3} flex={1}>
                  <Box as="span">{iconFor(e.type)}</Box>
                  <Text fontWeight="medium" color={text}>{e.type}</Text>
                  <Text color={muted} fontSize="sm" ml={2}>{e.meta}</Text>
                </HStack>
                <HStack align="center" spacing={2}>
                  <Badge colorScheme="blue" size="sm">{e.device}</Badge>
                  <Text color={muted} fontSize="xs">{e.time}</Text>
                </HStack>
              </Box>
            ))}
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}
