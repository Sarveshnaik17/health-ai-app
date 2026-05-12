import React, { useContext } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { ThemeContext } from '../../context/ThemeContext';

const DistributionChart = ({ data }) => {
  const { theme } = useContext(ThemeContext);
  const isDark = theme === 'dark';

  // Format data for Recharts
  const chartData = data?.map(item => ({
    name: item.category,
    value: item.count
  })) || [];

  const COLORS = {
    'Low': '#22c55e',
    'Moderate': '#eab308',
    'High': '#f97316',
    'Critical': '#ef4444',
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700 p-3 rounded-lg shadow-xl flex items-center gap-2">
          <div 
            className="w-3 h-3 rounded-full" 
            style={{ backgroundColor: payload[0].payload.fill }}
          />
          <span className="text-dark-900 dark:text-white font-medium">
            {payload[0].name}:
          </span>
          <span className="text-dark-500 dark:text-dark-400">
            {payload[0].value} tests
          </span>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64 w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
            stroke="none"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#3b82f6'} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="bottom" 
            height={36} 
            iconType="circle"
            formatter={(value) => <span className="text-dark-700 dark:text-dark-300 text-sm ml-1">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DistributionChart;
