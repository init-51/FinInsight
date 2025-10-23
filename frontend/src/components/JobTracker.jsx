import React, { useState, useEffect, useCallback } from 'react'
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  CircularProgress,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material'
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material'
import axios from 'axios'
import ResultsView from './ResultsView'

// Local development default; override VITE_API_URL in production to point at the deployed API
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const POLL_INTERVAL = 2000 // 2 seconds

export default function JobTracker({ onSuccess, onError }) {
  const [jobId, setJobId] = useState('')
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [polling, setPolling] = useState(false)
  const [statusError, setStatusError] = useState(null)

  const fetchStatus = useCallback(async (id) => {
    const normalizedId = id?.trim()
    if (!normalizedId) return null
    setLoading(true)
    try {
      const { data } = await axios.get(`${apiUrl}/jobs/status/${normalizedId}`)
      setStatus(data)
      setStatusError(null)
      return data
    } catch (err) {
      const message = err.response?.data?.detail || err.message
      onError?.(new Error(`Failed to fetch status: ${message}`))
      setStatusError(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [onError])

  const fetchResult = useCallback(async (id) => {
    const normalizedId = id?.trim()
    if (!normalizedId) return null
    setLoading(true)
    try {
      const { data } = await axios.get(`${apiUrl}/jobs/results/${normalizedId}`)
      setResult(data)
      if (data?.error) {
        const errorMessage = typeof data.error === 'string' ? data.error : 'Job failed'
        setStatusError(errorMessage)
        onError?.(new Error(errorMessage))
      } else if (data?.status === 'SUCCESS' && data?.result) {
        setStatusError(null)
        onSuccess?.(data)
      }
      return data
    } catch (err) {
      const message = err.response?.data?.detail || err.message
      onError?.(new Error(`Failed to fetch results: ${message}`))
      setStatusError(message)
      return null
    } finally {
      setLoading(false)
    }
  }, [onSuccess, onError])

  // Auto-polling effect
  useEffect(() => {
    let timer
    if (polling && jobId) {
      timer = setInterval(async () => {
        const s = await fetchStatus(jobId)
        if (s?.status === 'SUCCESS') {
          await fetchResult(jobId)
          setPolling(false)
        } else if (s?.status === 'FAILED' || s?.status === 'FAILURE') {
          setPolling(false)
          const failureMessage = s?.error || 'Job failed'
          setStatusError(failureMessage)
          onError?.(new Error(failureMessage))
        }
      }, POLL_INTERVAL)
    }
    return () => clearInterval(timer)
  }, [polling, jobId, fetchStatus, fetchResult, onError])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const normalizedId = jobId.trim()
    if (!normalizedId) return
    
    const s = await fetchStatus(normalizedId)
    if (s?.status === 'SUCCESS') {
      await fetchResult(normalizedId)
    } else if (s?.status === 'FAILED' || s?.status === 'FAILURE') {
      const failureMessage = s?.error || 'Job failed'
      setStatusError(failureMessage)
      onError?.(new Error(failureMessage))
    } else if (s) {
      setPolling(true)
      setStatusError(null)
    }
  }

  const getStatusColor = (status) => {
    if (!status) return 'default'
    switch (status.toLowerCase()) {
      case 'success': return 'success'
      case 'failed':
      case 'failure':
        return 'error'
      case 'pending': return 'warning'
      default: return 'default'
    }
  }

  return (
    <Paper elevation={0}>
      <Box component="form" onSubmit={handleSubmit} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Job Tracker
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            label="Job ID"
            value={jobId}
            onChange={(e) => {
              setJobId(e.target.value)
              setStatusError(null)
            }}
            fullWidth
            size="small"
            placeholder="Enter a job ID to track"
          />
          
          <Tooltip title="Check Once">
            <IconButton 
              onClick={() => fetchStatus(jobId)}
              disabled={!jobId || loading}
              color="primary"
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title={polling ? "Stop Polling" : "Start Polling"}>
            <IconButton
              onClick={() => setPolling(!polling)}
              disabled={!jobId || loading}
              color={polling ? "error" : "success"}
            >
              {polling ? <StopIcon /> : <PlayIcon />}
            </IconButton>
          </Tooltip>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}

        {statusError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {statusError}
          </Alert>
        )}

        {status && (
          <Box sx={{ mt: 2 }}>
            <Chip
              label={`Status: ${status.status}`}
              color={getStatusColor(status.status)}
              variant="outlined"
            />
          </Box>
        )}

        <ResultsView result={result} loading={loading && !result} />
      </Box>
    </Paper>
  )
}

