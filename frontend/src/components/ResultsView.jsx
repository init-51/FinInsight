import React, { useMemo } from 'react'
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  useTheme,
  Skeleton,
  Fade
} from '@mui/material'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

function MetricCard({ title, value, suffix = '', color = 'primary' }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h5" component="div" color={color}>
          {typeof value === 'number' ? value.toFixed(2) : value}
          {suffix}
        </Typography>
      </CardContent>
    </Card>
  )
}

function LoadingView() {
  return (
    <Paper elevation={0} sx={{ p: 3, mt: 3 }}>
      <Skeleton variant="text" width={300} height={32} sx={{ mb: 2 }} />
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card variant="outlined">
              <CardContent>
                <Skeleton variant="text" width={120} />
                <Skeleton variant="text" width={80} height={40} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ height: 400 }}>
        <Skeleton variant="rectangular" height="100%" />
      </Box>
    </Paper>
  )
}

export default function ResultsView({ result, loading }) {
  const theme = useTheme()
  
  if (loading) return <LoadingView />
  if (!result?.result) return null
  
  const r = result.result
  const returnPercentage = ((r.final_value - 10000) / 10000 * 100).toFixed(2)
  
  const chartData = useMemo(() => {
    const labels = r.timeseries.map(t => t.date)
    const data = r.timeseries.map(t => t.value)
    
    return {
      labels,
      datasets: [
        {
          label: 'Portfolio Value ($)',
          data,
          borderColor: theme.palette.primary.main,
          backgroundColor: `${theme.palette.primary.main}20`,
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHitRadius: 10,
          pointHoverRadius: 5,
          pointBackgroundColor: theme.palette.primary.main
        }
      ]
    }
  }, [r.timeseries, theme.palette.primary.main])

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'end'
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context) => `Value: $${context.parsed.y.toFixed(2)}`
        }
      }
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        beginAtZero: false,
        grid: {
          color: theme.palette.divider
        }
      }
    }
  }

  return (
    <Fade in timeout={500}>
      <Paper elevation={0} sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Results for {r.portfolio}
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Final Value"
              value={r.final_value}
              suffix="$"
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Total Return"
              value={returnPercentage}
              suffix="%"
              color={returnPercentage >= 0 ? "success" : "error"}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Sharpe Ratio"
              value={r.sharpe_ratio}
              color={r.sharpe_ratio >= 1 ? "success" : "warning"}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Volatility"
              value={r.volatility * 100}
              suffix="%"
              color={r.volatility <= 0.2 ? "success" : "warning"}
            />
          </Grid>
        </Grid>

        <Box sx={{ height: 400 }}>
          <Line data={chartData} options={chartOptions} />
        </Box>
      </Paper>
    </Fade>
  )
}
