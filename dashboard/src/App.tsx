import { Box, Container, Text, Link } from '@chakra-ui/react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout/Layout'
import { LiveFeed } from './components/LiveFeed/LiveFeed'
import { Dashboard } from './pages/Dashboard'
import { AlertPanel } from './components/AlertPanel/AlertPanel'
import { DeviceStatus } from './components/DeviceStatus/DeviceStatus'
import { EventLog } from './components/EventLog/EventLog'

export default function App() {
  return (
    <Layout>
      <Container maxW="7xl">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/live" element={<LiveFeed />} />
          <Route path="/alerts" element={<AlertPanel />} />
          <Route path="/devices" element={<DeviceStatus />} />
          <Route path="/events" element={<EventLog />} />
        </Routes>
      </Container>
      <Box as="footer" mt={8} pt={4} borderTop="1px solid" borderColor="gray.200">
        <Text textAlign="center" fontSize="sm" color="gray.500">
          Sentinel-X &nbsp;|&nbsp;
          <Link href="https://github.com" isExternal>GitHub</Link>&nbsp;|&nbsp;
          <Link href="/docs" isExternal>Docs</Link>
        </Text>
      </Box>
    </Layout>
  )
}
