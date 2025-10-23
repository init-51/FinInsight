import React, { useMemo, useState } from 'react'
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  IconButton,
  CircularProgress,
  Grid,
  Paper,
  Alert
} from '@mui/material'
import {
  Add as AddIcon,
  Remove as RemoveIcon
} from '@mui/icons-material'
import axios from 'axios'

// Local development default; production builds should set VITE_API_URL to the live backend URL
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function PortfolioForm({ onSuccess, onError }) {
  const [name, setName] = useState('My Portfolio')
  const [initial, setInitial] = useState(10000)
  const [startDate, setStartDate] = useState('2024-01-01')
  const [endDate, setEndDate] = useState('2024-12-31')
  const [assets, setAssets] = useState([{ ticker: 'AAPL', weight: 0.5 }])
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [initialError, setInitialError] = useState('')
  const [weightErrors, setWeightErrors] = useState({})
  const [formError, setFormError] = useState(null)

  function addAsset() {
    setAssets([...assets, { ticker: '', weight: 0 }])
    setFormError(null)
  }

  function removeAsset(index) {
    const updatedAssets = assets.filter((_, i) => i !== index)
    setAssets(updatedAssets)
    setFormError(null)
    setWeightErrors((prev) => {
      const updated = { ...prev }
      delete updated[index]
      const reordered = {}
      updatedAssets.forEach((_, newIdx) => {
        const sourceIdx = newIdx >= index ? newIdx + 1 : newIdx
          if (updated[sourceIdx]) {
            reordered[newIdx] = updated[sourceIdx]
          }
        })
      return reordered
    })
  }

  function updateAsset(i, key, value) {
    const copy = [...assets]
    copy[i][key] = value
    setAssets(copy)
    setFormError(null)

    if (key === 'weight') {
      const numeric = Number(value)
      let message = ''
      if (value === '') {
        message = 'Weight is required'
      } else if (Number.isNaN(numeric)) {
        message = 'Enter a numeric weight'
      } else if (numeric < 0 || numeric > 1) {
        message = 'Weight must be between 0 and 1'
      }
      setWeightErrors((prev) => ({ ...prev, [i]: message }))
    }
  }

  function handleInitialChange(e) {
    const value = e.target.value
    setInitial(value)
    setFormError(null)
    const numericValue = Number(value)
    if (value === '') {
      setInitialError('Initial value is required')
    } else if (Number.isNaN(numericValue) || numericValue <= 0) {
      setInitialError('Initial value must be greater than 0')
    } else {
      setInitialError('')
    }
  }

  async function submit(e) {
    e.preventDefault()
    if (!isFormValid) {
      setFormError('Please resolve validation errors before submitting.')
      return
    }
    setLoading(true)
    setFormError(null)
    try {
      const totalWeight = assets.reduce((sum, a) => sum + Number(a.weight), 0)
      if (Math.abs(totalWeight - 1) > 0.001) {
        setFormError('Asset weights must sum to 1.0')
        setLoading(false)
        return
      }

      const payload = {
        name,
        initial_value: Number(initial),
        start_date: startDate,
        end_date: endDate,
        assets: assets.map(a => ({ 
          ticker: a.ticker.toUpperCase(), 
          weight: Number(a.weight)
        }))
      }

      const { data } = await axios.post(
        `${apiUrl}/jobs/backtest`,
        { portfolio: payload },
        { headers: { 'Content-Type': 'application/json' }}
      )

      setJobId(data.job_id)
      onSuccess?.(data.job_id)

    } catch (err) {
      const message = err.response?.data?.detail || err.message
      onError?.(new Error(message))
    } finally {
      setLoading(false)
    }
  }

  const isFormValid = useMemo(() => {
    const initialValid = Number(initial) > 0 && !initialError
    const weightsValid =
      Object.values(weightErrors).every((msg) => !msg) &&
      assets.every((asset) => {
        const numeric = Number(asset.weight)
        return (
          asset.ticker &&
          !Number.isNaN(numeric) &&
          numeric >= 0 &&
          numeric <= 1
        )
      })

    return (
      !loading &&
      name &&
      initialValid &&
      startDate &&
      endDate &&
      assets.length > 0 &&
      weightsValid
    )
  }, [name, initial, initialError, startDate, endDate, assets, weightErrors, loading])

  return (
    <Paper elevation={0}>
      <Box component="form" onSubmit={submit} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Create Portfolio Backtest
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label="Portfolio Name"
              fullWidth
              value={name}
              onChange={e => setName(e.target.value)}
              required
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              label="Initial Value ($)"
              type="number"
              fullWidth
              value={initial}
              onChange={handleInitialChange}
              required
              inputProps={{ min: 0 }}
              error={Boolean(initialError)}
              helperText={initialError || ' '}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              label="Start Date"
              type="date"
              fullWidth
              value={startDate}
              onChange={e => setStartDate(e.target.value)}
              required
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              label="End Date"
              type="date"
              fullWidth
              value={endDate}
              onChange={e => setEndDate(e.target.value)}
              required
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
        </Grid>

        <Typography variant="subtitle1" sx={{ mt: 4, mb: 2 }}>
          Portfolio Assets
        </Typography>

        {assets.map((asset, i) => (
          <Box 
            key={i} 
            sx={{
              display: 'flex',
              gap: 2,
              mb: 2,
              alignItems: 'center'
            }}
          >
            <TextField
              label="Ticker"
              value={asset.ticker}
              onChange={e => updateAsset(i, 'ticker', e.target.value)}
              required
              sx={{ flex: 2 }}
            />
            <TextField
              label="Weight"
              type="number"
              value={asset.weight}
              onChange={e => updateAsset(i, 'weight', e.target.value)}
              required
              inputProps={{ 
                step: 0.1,
                min: 0,
                max: 1
              }}
              sx={{ flex: 1 }}
              error={Boolean(weightErrors[i])}
              helperText={weightErrors[i] || ' '}
            />
            <span>
              <IconButton 
                onClick={() => removeAsset(i)}
                disabled={assets.length === 1}
                color="error"
              >
                <RemoveIcon />
              </IconButton>
            </span>
          </Box>
        ))}

        {formError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {formError}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
          <Button
            startIcon={<AddIcon />}
            onClick={addAsset}
            variant="outlined"
          >
            Add Asset
          </Button>
          <Box sx={{ flex: 1 }} />
          <span>
            <Button
              type="submit"
              variant="contained"
              disabled={!isFormValid}
              startIcon={
                loading ? <CircularProgress size={20} color="inherit" /> : null
              }
            >
              {loading ? 'Submitting...' : 'Submit Backtest'}
            </Button>
          </span>
        </Box>

        {jobId && (
          <Typography sx={{ mt: 2 }} color="primary">
            Backtest job submitted successfully! ID: {jobId}
          </Typography>
        )}
      </Box>
    </Paper>
  )
}
