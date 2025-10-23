import React, { useEffect, useState } from 'react'
import {
  Box,
  CircularProgress,
  Alert,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'
import axios from 'axios'

// Local development fallback; production deployments must set VITE_API_URL appropriately
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function HistoryView() {
  const [historyData, setHistoryData] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true

    const fetchHistory = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const { data } = await axios.get(`${apiUrl}/jobs/history`)
        if (isMounted) {
          setHistoryData(Array.isArray(data) ? data : [])
        }
      } catch (err) {
        if (isMounted) {
          const message = err.response?.data?.detail || err.message || 'Failed to load backtest history'
          setError(message)
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    fetchHistory()
    return () => {
      isMounted = false
    }
  }, [])

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    )
  }

  if (!historyData.length) {
    return (
      <Paper elevation={0} sx={{ p: 3 }}>
        <Typography variant="body1">No backtest history found.</Typography>
      </Paper>
    )
  }

  return (
    <TableContainer component={Paper} elevation={0}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Portfolio Name</TableCell>
            <TableCell>Final Value</TableCell>
            <TableCell>Date Ran</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {historyData.map((item) => (
            <TableRow key={item.job_id}>
              <TableCell>{item.portfolio_name}</TableCell>
              <TableCell>${item.final_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</TableCell>
              <TableCell>{new Date(item.created_at).toLocaleString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
