import { Box, Grid, GridItem, Text, Stat, StatLabel, StatNumber, StatArrow, Card, CardBody, Badge } from '@chakra-ui/react'
import { TrendingUp, AlertCircle, Video, Users } from 'lucide-react'

export function Dashboard() {
  const stats = [
    { label: 'Active Cameras', value: '4', delta: '+2', icon: <Video size={20} />, color: 'green.500' },
    { label: 'Devices Online', value: '12', delta: '-1', icon: <Users size={20} />, color: 'blue.500' },
    { label: 'Alerts (24h)', value: '3', delta: '+1', icon: <AlertCircle size={20} />, color: 'orange.500' },
    { label: 'Events Today', value: '142', delta: '+12%', icon: <TrendingUp size={20} />, color: 'purple.500' },
  ]

  return (
    <Box>
      <Text fontSize="2xl" fontWeight="bold" mb={6}>Dashboard</Text>
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={6}>
        {stats.map((s) => (
          <GridItem key={s.label}>
            <Stat>
              <StatLabel fontSize="sm">{s.label}</StatLabel>
              <StatNumber>{s.value}</StatNumber>
              <StatArrow type={s.delta.startsWith('-') ? 'decrease' : 'increase'} color={s.color}>
                {s.delta}
              </StatArrow>
            </Stat>
          </GridItem>
        ))}
      </Grid>
      <Grid mt={8} templateColumns={{ base: '1fr', lg: 'repeat(2, 1fr)' }} gap={6}>
        <Card borderRadius="xl">
          <CardBody>
            <Text fontWeight="semantic" mb={4} fontSize="lg">
              System Status
            </Text>
            <Badge colorScheme="green">All systems operational</Badge>
          </CardBody>
        </Card>
        <Card borderRadius="xl">
          <CardBody>
            <Text fontWeight="semantic" mb={4} fontSize="lg">
              Recent Activity
            </Text>
            <Text fontSize="sm" color="gray.500">
              No recent activity. Connect the live feed to start monitoring.
            </Text>
          </CardBody>
        </Card>
      </Grid>
    </Box>
  )
}
