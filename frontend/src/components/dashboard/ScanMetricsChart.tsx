import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';

interface ScanMetricData {
  name: string;
  completed: number;
  failed: number;
  running: number;
  total: number;
}

interface ScanMetricsChartProps {
  data: ScanMetricData[];
  loading?: boolean;
  height?: number;
}

const ScanMetricsChart: React.FC<ScanMetricsChartProps> = ({
  data,
  loading = false,
  height = 300
}) => {
  const theme = useTheme();

  const colors = {
    completed: '#00C853',
    failed: '#FF4C4C',
    running: '#FFB833',
    total: '#4A90E2'
  };

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: 'rgba(10, 22, 40, 0.95)',
            border: '1px solid rgba(74, 144, 226, 0.3)',
            borderRadius: 1,
            p: 1.5,
            backdropFilter: 'blur(10px)'
          }}
        >
          <Typography variant="body2" sx={{ color: '#fff', mb: 1 }}>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color, fontSize: '0.875rem' }}
            >
              {entry.dataKey.charAt(0).toUpperCase() + entry.dataKey.slice(1)}: {entry.value}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Box
        sx={{
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(46, 46, 63, 0.1)',
          borderRadius: 1,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: '-100%',
            width: '100%',
            height: '100%',
            background: 'linear-gradient(90deg, transparent, rgba(74, 144, 226, 0.1), transparent)',
            animation: 'shimmer 1.5s infinite'
          }}
        />
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Loading chart data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(74, 144, 226, 0.1)"
            vertical={false}
          />
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
          />
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="completed"
            fill={colors.completed}
            radius={[2, 2, 0, 0]}
            name="Completed"
          />
          <Bar
            dataKey="running"
            fill={colors.running}
            radius={[2, 2, 0, 0]}
            name="Running"
          />
          <Bar
            dataKey="failed"
            fill={colors.failed}
            radius={[2, 2, 0, 0]}
            name="Failed"
          />
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ScanMetricsChart;