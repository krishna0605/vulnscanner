import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import { Box, Typography, useTheme } from '@mui/material';

interface ProjectDistributionData {
  name: string;
  value: number;
  color: string;
}

interface ProjectDistributionChartProps {
  data: ProjectDistributionData[];
  loading?: boolean;
  height?: number;
}

const ProjectDistributionChart: React.FC<ProjectDistributionChartProps> = ({
  data,
  loading = false,
  height = 300
}) => {
  const theme = useTheme();

  // Custom tooltip component
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
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
          <Typography variant="body2" sx={{ color: '#fff', mb: 0.5 }}>
            {data.name}
          </Typography>
          <Typography
            variant="body2"
            sx={{ color: data.color, fontSize: '0.875rem' }}
          >
            Count: {data.value}
          </Typography>
          <Typography
            variant="body2"
            sx={{ color: 'text.secondary', fontSize: '0.75rem' }}
          >
            {((data.value / data.total) * 100).toFixed(1)}%
          </Typography>
        </Box>
      );
    }
    return null;
  };

  // Custom label component
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    if (percent < 0.05) return null; // Don't show labels for slices smaller than 5%
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={12}
        fontWeight={500}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  // Custom legend component
  const CustomLegend = ({ payload }: any) => {
    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center', mt: 2 }}>
        {payload.map((entry: any, index: number) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5
            }}
          >
            <Box
              sx={{
                width: 12,
                height: 12,
                backgroundColor: entry.color,
                borderRadius: '50%'
              }}
            />
            <Typography
              variant="body2"
              sx={{
                color: theme.palette.text.secondary,
                fontSize: '0.75rem'
              }}
            >
              {entry.value}
            </Typography>
          </Box>
        ))}
      </Box>
    );
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

  // Calculate total for percentage calculation
  const dataWithTotal = data.map(item => ({
    ...item,
    total: data.reduce((sum, d) => sum + d.value, 0)
  }));

  return (
    <Box sx={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={dataWithTotal}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={80}
            innerRadius={40}
            fill="#8884d8"
            dataKey="value"
            stroke="none"
          >
            {dataWithTotal.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ProjectDistributionChart;