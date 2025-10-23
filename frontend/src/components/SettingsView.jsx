import React from 'react'
import { Container, Paper, Typography } from '@mui/material'

export default function SettingsView() {
  return (
    <Container maxWidth="md">
      <Paper elevation={0} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Settings page is under construction.
        </Typography>
      </Paper>
    </Container>
  )
}
