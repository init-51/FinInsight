import React, { useState, useMemo } from 'react'
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useMediaQuery,
  createTheme,
  ThemeProvider,
  Snackbar,
  Alert,
  Container,
  Paper
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Brightness4 as DarkIcon,
  Brightness7 as LightIcon
} from '@mui/icons-material'

import PortfolioForm from './components/PortfolioForm'
import JobTracker from './components/JobTracker'
import ResultsView from './components/ResultsView'
import HistoryView from './components/HistoryView'
import SettingsView from './components/SettingsView'

const DRAWER_WIDTH = 240

export default function App() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [activeSection, setActiveSection] = useState('dashboard')
  const [notification, setNotification] = useState(null)

  // Material UI responsive hooks
  const isMobile = useMediaQuery('(max-width:600px)')

  // Create theme with dark/light mode
  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode: darkMode ? 'dark' : 'light',
          primary: {
            main: '#1976d2',
          },
          secondary: {
            main: '#9c27b0',
          },
        },
      }),
    [darkMode]
  )

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const showNotification = (message, severity = 'success') => {
    setNotification({ message, severity })
  }

  const handleCloseNotification = () => {
    setNotification(null)
  }

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          FinInsight
        </Typography>
      </Toolbar>
      <List>
        <ListItem disablePadding>
          <ListItemButton
            selected={activeSection === 'dashboard'}
            onClick={() => setActiveSection('dashboard')}
          >
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={activeSection === 'backtests'}
            onClick={() => setActiveSection('backtests')}
          >
            <ListItemIcon>
              <AnalyticsIcon />
            </ListItemIcon>
            <ListItemText primary="Backtests" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton
            selected={activeSection === 'settings'}
            onClick={() => setActiveSection('settings')}
          >
            <ListItemIcon>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
              Portfolio Analysis
            </Typography>
            <Box sx={{ my: 4 }}>
              <Paper elevation={0} sx={{ p: 3 }}>
                <PortfolioForm
                  onSuccess={(jobId) => {
                    showNotification(`Backtest job ${jobId} submitted successfully`)
                  }}
                  onError={(error) => {
                    showNotification(error.message, 'error')
                  }}
                />
              </Paper>
            </Box>
            <Box sx={{ my: 4 }}>
              <Paper elevation={0} sx={{ p: 3 }}>
                <JobTracker
                  onSuccess={(result) => {
                    showNotification('Backtest completed successfully')
                  }}
                  onError={(error) => {
                    showNotification(error.message, 'error')
                  }}
                />
              </Paper>
            </Box>
          </Box>
        )
      case 'backtests':
        return (
          <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
              Backtest History
            </Typography>
            <HistoryView />
          </Box>
        )
      case 'settings':
        return (
          <Box sx={{ p: 3 }}>
            <SettingsView />
          </Box>
        )
      default:
        return null
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        
        {/* App Bar */}
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
            ml: { sm: `${DRAWER_WIDTH}px` },
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}
            </Typography>
            <IconButton 
              color="inherit" 
              onClick={() => setDarkMode(!darkMode)}
              aria-label="toggle dark mode"
            >
              {darkMode ? <LightIcon /> : <DarkIcon />}
            </IconButton>
          </Toolbar>
        </AppBar>

        {/* Sidebar */}
        <Box
          component="nav"
          sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
        >
          {/* Mobile drawer */}
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better mobile performance
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: DRAWER_WIDTH,
              },
            }}
          >
            {drawer}
          </Drawer>
          
          {/* Desktop drawer */}
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: DRAWER_WIDTH,
              },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>

        {/* Main content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          }}
        >
          <Toolbar /> {/* Spacer for AppBar */}
          <Container maxWidth="lg">
            {renderContent()}
          </Container>
        </Box>

        {/* Notifications */}
        <Snackbar
          open={!!notification}
          autoHideDuration={6000}
          onClose={handleCloseNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          {notification && (
            <Alert
              onClose={handleCloseNotification}
              severity={notification.severity}
              elevation={6}
              variant="filled"
            >
              {notification.message}
            </Alert>
          )}
        </Snackbar>
      </Box>
    </ThemeProvider>
  )
}
