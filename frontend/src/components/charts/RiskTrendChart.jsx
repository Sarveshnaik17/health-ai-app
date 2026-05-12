import React, { useContext } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ThemeContext } from '../../context/ThemeContext';

const RiskTrendChart = ({ data }) => {
  const { theme } = useContext(ThemeContext);
  const isDark = theme === 'dark';

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700 p-3 rounded-lg shadow-xl">
          <p className="text-dark-500 dark:text-dark-400 text-xs mb-1">{label}</p>
          <p className="text-blue-600 dark:text-blue-400 font-bold">
            Risk: {payload[0].value}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#334155' : '#e2e8f0'} vertical={false} />
          <XAxis 
            dataKey="day" 
            stroke={isDark ? '#64748b' : '#94a3b8'} 
            fontSize={12}
            tickLine={false}
            axisLine={false}
            dy={10}
          />
          <YAxis 
            stroke={isDark ? '#64748b' : '#94a3b8'} 
            fontSize={12}
            tickLine={false}
            axisLine={false}
            dx={-10}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="avg_risk" 
            stroke="#3b82f6" 
            strokeWidth={3}
            dot={{ r: 4, strokeWidth: 2, fill: isDark ? '#0f172a' : '#ffffff' }}
            activeDot={{ r: 6, strokeWidth: 0, fill: '#3b82f6' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskTrendChart;
