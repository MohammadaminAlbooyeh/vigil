import { Box, VStack, Text, Badge, Card, CardBody, HStack, useColorModeValue } from '@chakra-ui/react'
import { User } from 'lucide-react'

const DEVICES = [
  { id: 'cam-01', name: 'ESP32-CAM-01', type: 'camera', status: 'online', location: 'Front Door' },
  { id: 'cam-02', name: 'ESP32-CAM-02', type: 'camera', status: 'online', location: 'Back Yard' },
  { id: 's3-01', name: 'ESP32-S3-01', type: 'sensor', status: 'online', location: 'Living Room' },
  { id: 's3-02', name: 'ESP32-S3-02', type: 'sensor', status: 'offline', location: 'Garage' },
  { id: 'act-01', name: 'ESP32-Actuator-01', type: 'actuator', status: 'online', location: 'Main Gate' },
]

const statusColor = (s: string) => (s === 'online' ? 'green' : 'red')

export function DeviceStatus() {
  const text = useColorModeValue('gray.800', 'gray.100')
  const muted = useColorModeValue('gray.500', 'gray.400')

  return (
    <Box>
      <VStack align="start" spacing={4}>
        <Box as="span" fontSize="2xl" fontWeight="bold" color={text}>Devices</Box>
        <Text color={muted} fontSize="sm">Monitor and manage edge devices.</Text>
        <Card borderRadius="xl" mt={4}>
          <CardBody>
            {DEVICES.map((d) => (
              <Box key={d.id} py={3} borderBottom="1px solid" borderColor="gray.100" display="flex" alignItems="center" justifyContent="space-between">
                <HStack align="center" spacing={3} flex={1}>
                  <Box as="span">{d.type === 'camera' ? <VideoIcon /> : <User size={18} />}</Box>
                  <Text fontWeight="medium" color={text}>{d.name}</Text>
                  <Text color={muted} fontSize="sm" ml={2}>{d.location}</Text>
                </HStack>
                <Badge colorScheme={statusColor(d.status)} size="sm">{d.status}</Badge>
              </Box>
            ))}
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

function VideoIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" {...props}>
      <polygon points="11 2 6 2 2 10 2 14 6 14 11 14 11 18 11 18 16 18 16 18 22 6 22 6 18 2 18 2 6 22 6 22 2 11 2 11 18 2 18 2 22 6 22 6 14 11 14 11 10 11 10 6 14 6 14 2 11 2" />
    </svg>
  )
}
