import React, { useState, useEffect } from 'react';
import { Download, FileText, Filter, Search } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import api from '../utils/api';

const Reports = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloadingCsv, setDownloadingCsv] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchPredictions();
  }, [page]);

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/predictions?page=${page}&per_page=15`);
      if (res.data.status === 'success') {
        setPredictions(res.data.data.predictions);
        setTotalPages(res.data.data.total_pages);
      }
    } catch (error) {
      console.error("Failed to fetch predictions", error);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (type) => {
    const isCsv = type === 'csv';
    isCsv ? setDownloadingCsv(true) : setDownloadingPdf(true);
    
    try {
      const response = await api.get(`/reports/${type}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, '');
      link.setAttribute('download', `medivision_report_${dateStr}.${type}`);
      
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      console.error(`Failed to download ${type}`, error);
      alert(`Failed to download ${type.toUpperCase()} report. Please try again.`);
    } finally {
      isCsv ? setDownloadingCsv(false) : setDownloadingPdf(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-dark-900 dark:text-white">Reports & History</h1>
          <p className="text-dark-500 dark:text-dark-400 mt-1 text-sm">View, filter, and export your assessment data.</p>
        </div>
        
        <div className="flex gap-3 w-full sm:w-auto">
          <button 
            onClick={() => downloadReport('csv')}
            disabled={downloadingCsv}
            className="flex-1 sm:flex-none btn-secondary bg-white dark:bg-dark-900 shadow-sm"
          >
            {downloadingCsv ? (
              <div className="w-4 h-4 border-2 border-dark-300 border-t-blue-500 rounded-full animate-spin" />
            ) : <Download className="w-4 h-4" />}
            Export CSV
          </button>
          
          <button 
            onClick={() => downloadReport('pdf')}
            disabled={downloadingPdf}
            className="flex-1 sm:flex-none btn-primary"
          >
            {downloadingPdf ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : <FileText className="w-4 h-4" />}
            Generate PDF
          </button>
        </div>
      </div>

      <GlassCard padding="p-0" className="overflow-hidden">
        <div className="p-4 border-b border-dark-200 dark:border-dark-800 bg-dark-50/50 dark:bg-dark-900/50 flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-dark-400 absolute left-3 top-3" />
            <input 
              type="text" 
              placeholder="Search history..." 
              className="w-full bg-white dark:bg-dark-950 border border-dark-200 dark:border-dark-700 text-sm rounded-lg pl-9 pr-3 py-2.5 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button className="flex items-center justify-center gap-2 px-4 py-2 bg-white dark:bg-dark-950 border border-dark-200 dark:border-dark-700 rounded-lg text-sm text-dark-600 dark:text-dark-300 hover:bg-dark-50 dark:hover:bg-dark-800 transition-colors">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>

        <div className="overflow-x-auto min-h-[400px]">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            </div>
          ) : predictions.length > 0 ? (
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-dark-500 bg-white dark:bg-dark-950 uppercase border-b border-dark-200 dark:border-dark-800">
                <tr>
                  <th className="px-6 py-4 font-medium">Date & Time</th>
                  <th className="px-6 py-4 font-medium">Risk Level</th>
                  <th className="px-6 py-4 font-medium">Score</th>
                  <th className="px-6 py-4 font-medium">Inputs Summary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-200 dark:divide-dark-800 bg-transparent">
                {predictions.map((item, idx) => (
                  <tr key={idx} className="hover:bg-dark-50/50 dark:hover:bg-dark-800/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-dark-900 dark:text-white">
                      {new Date(item.timestamp).toLocaleString(undefined, {
                        dateStyle: 'medium', timeStyle: 'short'
                      })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-1.5 rounded-full text-xs font-medium border ${
                        item.risk === 'High Risk' 
                          ? 'bg-red-50 border-red-200 text-red-700 dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-400'
                          : 'bg-green-50 border-green-200 text-green-700 dark:bg-green-500/10 dark:border-green-500/20 dark:text-green-400'
                      }`}>
                        {item.risk}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-dark-700 dark:text-dark-300">
                          {item.probability.toFixed(1)}%
                        </span>
                        <div className="w-16 h-1.5 rounded-full bg-dark-100 dark:bg-dark-800 overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${item.risk === 'High Risk' ? 'bg-red-500' : 'bg-green-500'}`}
                            style={{ width: `${item.probability}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-dark-500 dark:text-dark-400 truncate max-w-xs">
                      Age: {item.input_data?.Age}, BMI: {item.input_data?.BMI}, Gluc: {item.input_data?.Glucose}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-dark-500">
              <FileText className="w-12 h-12 text-dark-300 mb-3" />
              <p>No historical records found.</p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-dark-200 dark:border-dark-800 flex justify-between items-center bg-white dark:bg-dark-950">
            <span className="text-sm text-dark-500">
              Page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button 
                disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
                className="px-3 py-1 rounded border border-dark-200 dark:border-dark-700 text-sm hover:bg-dark-50 dark:hover:bg-dark-800 disabled:opacity-50 transition-colors"
              >
                Previous
              </button>
              <button 
                disabled={page === totalPages}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1 rounded border border-dark-200 dark:border-dark-700 text-sm hover:bg-dark-50 dark:hover:bg-dark-800 disabled:opacity-50 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </GlassCard>
    </div>
  );
};

export default Reports;
