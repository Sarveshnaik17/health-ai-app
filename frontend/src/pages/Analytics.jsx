import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from 'recharts';
import { Cpu, Server, Database, BrainCircuit, Activity } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import api from '../utils/api';

const Analytics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await api.get('/dashboard/model');
        if (res.data.status === 'success') {
          setMetrics(res.data.data);
        }
      } catch (error) {
        console.error("Failed to fetch model metrics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[60vh]">
        <div className="w-12 h-12 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] text-dark-500">
        <Activity className="w-16 h-16 text-dark-300 mb-4" />
        <h2 className="text-xl font-bold text-dark-900 dark:text-white mb-2">Model Data Unavailable</h2>
        <p>The machine learning model metrics could not be loaded.</p>
      </div>
    );
  }

  // Format feature importance for chart
  const importanceData = Object.entries(metrics.feature_importance || {})
    .map(([name, value]) => ({
      name: name.replace(/_/g, ' '),
      value: value * 100 // Convert to percentage
    }))
    .slice(0, 8); // Top 8 features

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700 p-3 rounded-lg shadow-xl">
          <p className="text-dark-900 dark:text-white font-medium mb-1">{payload[0].payload.name}</p>
          <p className="text-blue-600 dark:text-blue-400">
            Importance: {payload[0].value.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-bold text-dark-900 dark:text-white flex items-center gap-2">
          <BrainCircuit className="w-6 h-6 text-blue-500" />
          Model Analytics
        </h1>
        <p className="text-dark-500 dark:text-dark-400 mt-1 text-sm">
          Deep dive into the machine learning ensemble performance and feature insights.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard padding="p-5" className="flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-500 rounded-xl">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-dark-500 dark:text-dark-400">Model Type</p>
            <p className="text-lg font-bold text-dark-900 dark:text-white">Voting Ensemble</p>
          </div>
        </GlassCard>

        <GlassCard padding="p-5" className="flex items-center gap-4">
          <div className="p-3 bg-cyan-500/10 text-cyan-500 rounded-xl">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-dark-500 dark:text-dark-400">Training Samples</p>
            <p className="text-lg font-bold text-dark-900 dark:text-white">{metrics.dataset_size}</p>
          </div>
        </GlassCard>

        <GlassCard padding="p-5" className="flex items-center gap-4">
          <div className="p-3 bg-indigo-500/10 text-indigo-500 rounded-xl">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm text-dark-500 dark:text-dark-400">Last Trained</p>
            <p className="text-lg font-bold text-dark-900 dark:text-white">
              {new Date(metrics.trained_at).toLocaleDateString()}
            </p>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Metrics */}
        <GlassCard className="h-full">
          <h2 className="text-lg font-semibold text-dark-900 dark:text-white mb-6">Evaluation Metrics</h2>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-dark-700 dark:text-dark-300 font-medium">Accuracy</span>
                <span className="font-bold text-blue-500">{(metrics.metrics.accuracy * 100).toFixed(2)}%</span>
              </div>
              <div className="w-full h-2.5 bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: `${metrics.metrics.accuracy * 100}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-dark-700 dark:text-dark-300 font-medium">F1 Score</span>
                <span className="font-bold text-cyan-500">{(metrics.metrics.f1_score * 100).toFixed(2)}%</span>
              </div>
              <div className="w-full h-2.5 bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${metrics.metrics.f1_score * 100}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-dark-700 dark:text-dark-300 font-medium">ROC-AUC</span>
                <span className="font-bold text-indigo-500">{(metrics.metrics.roc_auc * 100).toFixed(2)}%</span>
              </div>
              <div className="w-full h-2.5 bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${metrics.metrics.roc_auc * 100}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-dark-700 dark:text-dark-300 font-medium">Precision</span>
                <span className="font-bold text-purple-500">{(metrics.metrics.precision * 100).toFixed(2)}%</span>
              </div>
              <div className="w-full h-2.5 bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                <div className="h-full bg-purple-500 rounded-full" style={{ width: `${metrics.metrics.precision * 100}%` }} />
              </div>
            </div>
            
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-dark-700 dark:text-dark-300 font-medium">Recall (Sensitivity)</span>
                <span className="font-bold text-pink-500">{(metrics.metrics.recall * 100).toFixed(2)}%</span>
              </div>
              <div className="w-full h-2.5 bg-dark-100 dark:bg-dark-800 rounded-full overflow-hidden">
                <div className="h-full bg-pink-500 rounded-full" style={{ width: `${metrics.metrics.recall * 100}%` }} />
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Feature Importance Chart */}
        <GlassCard className="h-full flex flex-col">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-dark-900 dark:text-white">Feature Importance</h2>
            <p className="text-sm text-dark-500 dark:text-dark-400">Relative impact of clinical metrics on predictions</p>
          </div>
          
          <div className="flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={importanceData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#334155" opacity={0.5} />
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  width={100}
                />
                <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={16}>
                  {importanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={`hsl(217, 91%, ${60 - (index * 4)}%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

export default Analytics;
