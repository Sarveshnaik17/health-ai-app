import React from 'react';
import GlassCard from './GlassCard';

const StatsCard = ({ title, value, icon: Icon, trend, trendValue, colorClass }) => {
  return (
    <GlassCard padding="p-5" className="flex flex-col">
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-xl ${colorClass} bg-opacity-10`}>
          <Icon className={`w-6 h-6 ${colorClass.replace('bg-', 'text-')}`} />
        </div>
        {trend && (
          <span className={`text-sm font-medium px-2 py-1 rounded-full ${
            trend === 'up' ? 'bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400' : 
            trend === 'down' ? 'bg-green-50 text-green-600 dark:bg-green-500/10 dark:text-green-400' : 
            'bg-dark-100 text-dark-600 dark:bg-dark-800 dark:text-dark-400'
          }`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '−'} {trendValue}
          </span>
        )}
      </div>
      <div>
        <h3 className="text-dark-500 dark:text-dark-400 font-medium text-sm mb-1">{title}</h3>
        <p className="text-3xl font-bold text-dark-900 dark:text-white tracking-tight">{value}</p>
      </div>
    </GlassCard>
  );
};

export default StatsCard;
