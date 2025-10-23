import React, { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  Stack,
  Button,
  Snackbar,
  Alert
} from '@mui/material'

const STORAGE_KEYS = ['fininsight:lastBacktestPayload', 'fininsight:lastTrackedJob']

export default function SettingsView() {
  const [notification, setNotification] = useState(null)

  const clearLocalState = () => {
    STORAGE_KEYS.forEach((key) => localStorage.removeItem(key))
    setNotification({ severity: 'success', message: 'Local application cache cleared.' })
  }

  return (
    <Container maxWidth='sm'>
      <Paper elevation={0} sx={{ p: 4 }}>
        <Typography variant='h5' gutterBottom>
          Settings
        </Typography>
        <Typography variant='body2' color='text.secondary' gutterBottom>
          Manage local preferences stored by the dashboard. Server configuration and secrets are managed through Render/Vercel environment variables.
        </Typography>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <Button variant='outlined' color='warning' onClick={clearLocalState}>
            Clear cached payloads
          </Button>
        </Stack>
      </Paper>

      <Snackbar
        open={!!notification}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {notification && (
          <Alert severity={notification.severity} onClose={() => setNotification(null)} sx={{ width: '100%' }}>
            {notification.message}
          </Alert>
        )}
      </Snackbar>
    </Container>
  )
}
