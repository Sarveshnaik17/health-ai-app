import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, CheckCircle, TrendingUp, Calendar, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';
import GlassCard from '../components/ui/GlassCard';
import StatsCard from '../components/ui/StatsCard';
import RiskTrendChart from '../components/charts/RiskTrendChart';
import DistributionChart from '../components/charts/DistributionChart';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [overviewRes, insightsRes] = await Promise.all([
          api.get('/dashboard/overview'),
          api.get('/dashboard/insights')
        ]);
        
        if (overviewRes.data.status === 'success') {
          setData(overviewRes.data.data);
        }
        if (insightsRes.data.status === 'success') {
          setInsights(insightsRes.data.data.insights);
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col space-y-6 animate-pulse">
        <div className="h-10 bg-dark-200 dark:bg-dark-800 rounded w-1/4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-dark-200 dark:bg-dark-800 rounded-2xl"></div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-80 bg-dark-200 dark:bg-dark-800 rounded-2xl"></div>
          <div className="h-80 bg-dark-200 dark:bg-dark-800 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  const { stats, recent_activity, weekly_trend } = data || {};

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-dark-900 dark:text-white">
            Welcome back, {user?.full_name?.split(' ')[0] || user?.username}
          </h1>
          <p className="text-dark-500 dark:text-dark-400 text-sm mt-1">
            Here's your health monitoring overview for today.
          </p>
        </div>
        <Link to="/predict" className="btn-primary shrink-0 self-start md:self-auto">
          <Activity className="w-5 h-5" />
          New Assessment
        </Link>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
          title="Total Assessments" 
          value={stats?.total_predictions || 0} 
          icon={Activity}
          colorClass="bg-blue-500 text-blue-500"
        />
        <StatsCard 
          title="High Risk Cases" 
          value={stats?.high_risk_count || 0} 
          icon={AlertTriangle}
          colorClass="bg-red-500 text-red-500"
        />
        <StatsCard 
          title="Low Risk Cases" 
          value={stats?.low_risk_count || 0} 
          icon={CheckCircle}
          colorClass="bg-green-500 text-green-500"
        />
        <StatsCard 
          title="Average Risk" 
          value={`${stats?.avg_probability || 0}%`} 
          icon={TrendingUp}
          colorClass="bg-cyan-500 text-cyan-500"
          trend={stats?.avg_probability > 50 ? 'up' : 'down'}
          trendValue={stats?.avg_probability > 50 ? 'High' : 'Normal'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="lg:col-span-2">
          <GlassCard delay={0.1} className="h-full flex flex-col">
            <h2 className="text-lg font-semibold text-dark-900 dark:text-white mb-2">Weekly Risk Trend</h2>
            <p className="text-sm text-dark-500 mb-6">Average probability score over the last 7 days</p>
            <div className="flex-1 min-h-[250px]">
              {weekly_trend && weekly_trend.length > 0 ? (
                <RiskTrendChart data={weekly_trend} />
              ) : (
                <div className="h-full flex items-center justify-center text-dark-400 text-sm">
                  Not enough data to display trend
                </div>
              )}
            </div>
          </GlassCard>
        </div>

        {/* AI Insights */}
        <div>
          <GlassCard delay={0.2} className="h-full flex flex-col">
            <h2 className="text-lg font-semibold text-dark-900 dark:text-white mb-4">AI Insights</h2>
            <div className="flex-1 space-y-4 overflow-y-auto pr-2">
              {insights.map((insight, idx) => (
                <div key={idx} className={`p-4 rounded-xl border ${
                  insight.type === 'warning' ? 'bg-red-50 border-red-100 dark:bg-red-500/5 dark:border-red-500/10' :
                  insight.type === 'success' ? 'bg-green-50 border-green-100 dark:bg-green-500/5 dark:border-green-500/10' :
                  'bg-blue-50 border-blue-100 dark:bg-blue-500/5 dark:border-blue-500/10'
                }`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span>{insight.icon}</span>
                    <h3 className={`text-sm font-semibold ${
                      insight.type === 'warning' ? 'text-red-700 dark:text-red-400' :
                      insight.type === 'success' ? 'text-green-700 dark:text-green-400' :
                      'text-blue-700 dark:text-blue-400'
                    }`}>{insight.title}</h3>
                  </div>
                  <p className="text-xs text-dark-600 dark:text-dark-300 mt-2 leading-relaxed">
                    {insight.description}
                  </p>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <GlassCard delay={0.3} padding="p-0">
            <div className="p-6 border-b border-dark-200 dark:border-dark-800 flex justify-between items-center">
              <h2 className="text-lg font-semibold text-dark-900 dark:text-white">Recent Assessments</h2>
              <Link to="/reports" className="text-sm text-blue-500 hover:text-blue-600 font-medium flex items-center gap-1">
                View All <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="overflow-x-auto">
              {recent_activity && recent_activity.length > 0 ? (
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-dark-500 bg-dark-50 dark:bg-dark-900/50 uppercase">
                    <tr>
                      <th className="px-6 py-4 font-medium">Date</th>
                      <th className="px-6 py-4 font-medium">Risk Level</th>
                      <th className="px-6 py-4 font-medium">Score</th>
                      <th className="px-6 py-4 font-medium">Category</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-200 dark:divide-dark-800">
                    {recent_activity.map((item, idx) => (
                      <tr key={idx} className="hover:bg-dark-50 dark:hover:bg-dark-800/50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-dark-900 dark:text-white flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-dark-400" />
                          {new Date(item.timestamp).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                            item.risk === 'High Risk' 
                              ? 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400'
                              : 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400'
                          }`}>
                            {item.risk}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-dark-600 dark:text-dark-300 font-mono">
                          {item.probability.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-dark-600 dark:text-dark-300">
                          {item.risk_category}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="p-8 text-center text-dark-500">
                  No assessments found. Run a prediction to see it here.
                </div>
              )}
            </div>
          </GlassCard>
        </div>

        {/* Risk Distribution */}
        <div>
          <GlassCard delay={0.4} className="h-full">
             <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-semibold text-dark-900 dark:text-white">Risk Distribution</h2>
             </div>
             {api && api.length > 0 ? (
                <div className="h-64 flex items-center justify-center text-dark-500">
                  <DistributionChart data={[]} />
                </div>
             ) : (
                <div className="h-64 flex items-center justify-center text-dark-400 text-sm bg-dark-50 dark:bg-dark-900/30 rounded-xl border border-dashed border-dark-200 dark:border-dark-700">
                  Data unavailable
                </div>
             )}
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
