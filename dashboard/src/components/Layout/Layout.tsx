import { Box, Flex, HStack, IconButton, useColorModeValue } from '@chakra-ui/react'
import { Menu, Shield, User, LayoutDashboard, BarChart3, Settings } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

export function Layout({ children }: { children: React.ReactNode }) {
  const bg = useColorModeValue('gray.50', 'gray.900')
  const text = useColorModeValue('gray.800', 'gray.100')
  const navigate = useNavigate()

  const menuItems = [
    { label: 'Dashboard', to: '/', icon: <LayoutDashboard size={18} /> },
    { label: 'Live Feed', to: '/live', icon: <BarChart3 size={18} /> },
    { label: 'Alerts', to: '/alerts', icon: <Shield size={18} /> },
    { label: 'Devices', to: '/devices', icon: <User size={18} /> },
    { label: 'Events', to: '/events', icon: <Menu size={18} /> },
    { label: 'Settings', to: '/settings', icon: <Settings size={18} /> },
  ]

  return (
    <Box bg={bg} minH="100vh" color={text} transition="background-color 0.2s">
      <Flex
        as="header"
        h="12"
        px={6}
        bg={useColorModeValue('white', 'gray.800')}
        borderBottom="1px solid"
        borderColor={useColorModeValue('gray.200', 'gray.700')}
        align="center"
        justify="space-between"
        position="sticky"
        top={0}
        zIndex={100}
      >
        <HStack align="center" gap={3}>
          <Box as="span" fontSize="xl" fontWeight="bold" letterSpacing="tight">
            Sentinel-X
          </Box>
        </HStack>
        <HStack align="center" gap={2}>
          {menuItems.map((item) => (
            <Link key={item.label} to={item.to} onClick={() => navigate(item.to)}>
              <IconButton
                icon={item.icon}
                aria-label={item.label}
                size="sm"
                variant="ghost"
              />
            </Link>
          ))}
        </HStack>
      </Flex>
      <Box px={6} py={4}>
        {children}
      </Box>
    </Box>
  )
}
