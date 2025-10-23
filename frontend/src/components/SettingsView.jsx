import React, { useMemo, useState } from "react"
import {
  Container,
  Paper,
  Typography,
  Grid,
  Stack,
  Button,
  Chip,
  Divider,
  TextField,
  Snackbar,
  Alert
} from "@mui/material"
import ContentCopyIcon from "@mui/icons-material/ContentCopy"
import RefreshIcon from "@mui/icons-material/Refresh"

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"

const STORAGE_KEYS = ["fininsight:lastBacktestPayload", "fininsight:lastTrackedJob"]

export default function SettingsView() {
  const [healthResult, setHealthResult] = useState({ status: "idle" })
  const [historyResult, setHistoryResult] = useState({ status: "idle" })
  const [notification, setNotification] = useState(null)

  const closeNotification = () => setNotification(null)

  const healthChip = useMemo(() => {
    switch (healthResult.status) {
      case "loading":
        return <Chip color="warning" label="Checking…" size="small" />
      case "success":
        return <Chip color="success" label="Healthy" size="small" />
      case "error":
        return <Chip color="error" label="Error" size="small" />
      default:
        return <Chip color="default" label="Not checked" size="small" />
    }
  }, [healthResult.status])

  const historyChip = useMemo(() => {
    switch (historyResult.status) {
      case "loading":
        return <Chip color="warning" label="Checking…" size="small" />
      case "success":
        return <Chip color="success" label={`${historyResult.count} jobs found`} size="small" />
      case "error":
        return <Chip color="error" label="Error" size="small" />
      default:
        return <Chip color="default" label="Not checked" size="small" />
    }
  }, [historyResult])

  const runHealthCheck = async () => {
    setHealthResult({ status: "loading" })
    try {
      const response = await fetch(`${apiUrl}/health`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const payload = await response.json()
      setHealthResult({ status: "success", payload })
    } catch (err) {
      setHealthResult({ status: "error", message: err.message })
      setNotification({ severity: "error", message: `Health check failed: ${err.message}` })
    }
  }

  const runHistoryCheck = async () => {
    setHistoryResult({ status: "loading" })
    try {
      const response = await fetch(`${apiUrl}/jobs/history`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const payload = await response.json()
      setHistoryResult({ status: "success", count: Array.isArray(payload) ? payload.length : 0 })
    } catch (err) {
      setHistoryResult({ status: "error", message: err.message })
      setNotification({ severity: "error", message: `History request failed: ${err.message}` })
    }
  }

  const copyApiUrl = async () => {
    try {
      await navigator.clipboard.writeText(apiUrl)
      setNotification({ severity: "success", message: "API URL copied to clipboard" })
    } catch (err) {
      setNotification({ severity: "error", message: "Copy failed. Select and copy manually." })
    }
  }

  const clearStoredPreferences = () => {
    STORAGE_KEYS.forEach((key) => localStorage.removeItem(key))
    setNotification({ severity: "success", message: "Local FinInsight preferences cleared" })
  }

  return (
    <Container maxWidth="lg">
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={0} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
              Environment
            </Typography>
            <Typography variant="body2" color="text.secondary">
              The dashboard reads environment configuration from Vercel at build time.
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Stack spacing={2}>
              <TextField
                label="API Base URL"
                value={apiUrl}
                InputProps={{ readOnly: true }}
                size="small"
              />
              <Stack direction="row" spacing={1}>
                <Button startIcon={<ContentCopyIcon />} onClick={copyApiUrl} variant="outlined">
                  Copy URL
                </Button>
                <Button startIcon={<RefreshIcon />} onClick={runHealthCheck} variant="outlined">
                  Check API Health
                </Button>
                {healthChip}
              </Stack>
              {healthResult.status === "success" && (
                <Typography variant="body2" color="text.secondary">
                  API response: {JSON.stringify(healthResult.payload)}
                </Typography>
              )}
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={0} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
              Job History Checks
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Validate that history endpoints respond correctly before sending users to the dashboard.
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Stack spacing={2}>
              <Stack direction="row" spacing={1}>
                <Button variant="outlined" onClick={runHistoryCheck} startIcon={<RefreshIcon />}>
                  Test History Endpoint
                </Button>
                {historyChip}
              </Stack>
              {historyResult.status === "success" && (
                <Typography variant="body2" color="text.secondary">
                  Latest response returned {historyResult.count} records.
                </Typography>
              )}
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={0} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
              Local Preferences
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Dependent components persist some client-side data. Clear it if you need to reset the experience.
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" color="warning" onClick={clearStoredPreferences}>
                Clear cached payloads
              </Button>
            </Stack>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={0} sx={{ p: 4 }}>
            <Typography variant="h5" gutterBottom>
              Deployment Notes
            </Typography>
            <Typography variant="body2" color="text.secondary">
              CORS values are controlled via the ALLOWED_ORIGINS environment variable on Render.
              Update it when your Vercel domain changes.
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2">
              1. Update the Render secret <strong>ALLOWED_ORIGINS</strong>.
            </Typography>
            <Typography variant="body2">
              2. Redeploy the API (Manual Deploy → Deploy latest commit).
            </Typography>
            <Typography variant="body2">
              3. Redeploy the Vercel frontend if you change build-time env vars.
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Snackbar
        open={!!notification}
        autoHideDuration={5000}
        onClose={closeNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {notification && (
          <Alert severity={notification.severity} onClose={closeNotification} sx={{ width: '100%' }}>
            {notification.message}
          </Alert>
        )}
      </Snackbar>
    </Container>
  )
}
