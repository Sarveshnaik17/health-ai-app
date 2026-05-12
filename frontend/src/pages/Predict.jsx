import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, AlertCircle, CheckCircle, HelpCircle, ArrowRight, RefreshCw } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import api from '../utils/api';

const Predict = () => {
  const [formData, setFormData] = useState({
    Pregnancies: 0,
    Glucose: 110,
    BloodPressure: 80,
    SkinThickness: 20,
    Insulin: 80,
    BMI: 25.0,
    DiabetesPedigreeFunction: 0.5,
    Age: 30
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const res = await api.post('/predict', formData);
      if (res.data.status === 'success') {
        setResult(res.data.data);
      } else {
        setError(res.data.error || 'Prediction failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred connecting to the server');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setResult(null);
  };

  const inputFields = [
    { name: 'Age', label: 'Age (years)', min: 1, max: 120, step: 1, desc: 'Patient age' },
    { name: 'Pregnancies', label: 'Pregnancies', min: 0, max: 20, step: 1, desc: 'Number of times pregnant' },
    { name: 'Glucose', label: 'Glucose (mg/dL)', min: 0, max: 300, step: 1, desc: 'Plasma glucose concentration' },
    { name: 'BloodPressure', label: 'Blood Pressure (mm Hg)', min: 0, max: 200, step: 1, desc: 'Diastolic blood pressure' },
    { name: 'SkinThickness', label: 'Skin Thickness (mm)', min: 0, max: 100, step: 1, desc: 'Triceps skin fold thickness' },
    { name: 'Insulin', label: 'Insulin (mu U/ml)', min: 0, max: 800, step: 1, desc: '2-Hour serum insulin' },
    { name: 'BMI', label: 'BMI', min: 0, max: 70, step: 0.1, desc: 'Body mass index (weight in kg/(height in m)^2)' },
    { name: 'DiabetesPedigreeFunction', label: 'Diabetes Pedigree Function', min: 0, max: 3.0, step: 0.01, desc: 'Diabetes pedigree function' },
  ];

  return (
    <div className="max-w-5xl mx-auto pb-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-dark-900 dark:text-white flex items-center gap-2">
          <Activity className="w-6 h-6 text-blue-500" /> 
          Health Risk Prediction
        </h1>
        <p className="text-dark-500 dark:text-dark-400 mt-2">
          Enter patient metrics below to run the advanced ensemble machine learning model.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Section */}
        <div className={`lg:col-span-7 transition-all duration-500`}>
          <GlassCard>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-5">
                {inputFields.map((field) => (
                  <div key={field.name} className="relative group">
                    <div className="flex justify-between items-center mb-1">
                      <label htmlFor={field.name} className="text-sm font-medium text-dark-700 dark:text-dark-300">
                        {field.label}
                      </label>
                      <div className="relative">
                        <HelpCircle className="w-4 h-4 text-dark-400 cursor-help" />
                        <div className="absolute right-0 bottom-full mb-2 w-48 p-2 bg-dark-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 shadow-xl">
                          {field.desc}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <input
                        type="range"
                        id={`${field.name}-slider`}
                        name={field.name}
                        min={field.min}
                        max={field.max}
                        step={field.step}
                        value={formData[field.name]}
                        onChange={handleChange}
                        className="flex-1 h-2 bg-dark-200 dark:bg-dark-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                      />
                      <input
                        type="number"
                        id={field.name}
                        name={field.name}
                        min={field.min}
                        max={field.max}
                        step={field.step}
                        value={formData[field.name]}
                        onChange={handleChange}
                        className="w-20 text-center bg-white dark:bg-dark-900 border border-dark-200 dark:border-dark-700 rounded-lg py-1 text-sm text-dark-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {error && (
                <div className="mt-6 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 text-red-600 dark:text-red-400 px-4 py-3 rounded-xl flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              <div className="mt-8 pt-6 border-t border-dark-200 dark:border-dark-800 flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full md:w-auto"
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Analyzing...
                    </div>
                  ) : (
                    <>Run ML Analysis <ArrowRight className="w-4 h-4 ml-1" /></>
                  )}
                </button>
              </div>
            </form>
          </GlassCard>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-5">
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.4 }}
              >
                <GlassCard className="relative overflow-hidden">
                  {/* Result Header */}
                  <div className="text-center mb-8 relative z-10">
                    <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 shadow-xl shadow-[${result.risk_category.color}]/20`}
                         style={{ backgroundColor: `${result.risk_category.color}20`, color: result.risk_category.color }}>
                      {result.prediction === 1 ? <AlertCircle className="w-10 h-10" /> : <CheckCircle className="w-10 h-10" />}
                    </div>
                    <h2 className="text-3xl font-bold text-dark-900 dark:text-white mb-2">
                      {result.risk_label}
                    </h2>
                    <p className="text-dark-500 text-sm px-4">
                      {result.risk_category.description}
                    </p>
                  </div>

                  {/* Score Meter */}
                  <div className="mb-8 relative z-10">
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-dark-600 dark:text-dark-400 font-medium">Risk Score</span>
                      <span className="font-bold text-dark-900 dark:text-white">{result.probability.toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-3 bg-dark-200 dark:bg-dark-700 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${result.probability}%` }}
                        transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
                        className="h-full rounded-full"
                        style={{ backgroundColor: result.risk_category.color }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-dark-400 mt-1">
                      <span>Low</span>
                      <span>Mod</span>
                      <span>High</span>
                      <span>Crit</span>
                    </div>
                  </div>

                  {/* Recommendations */}
                  {result.recommendations && result.recommendations.length > 0 && (
                    <div className="mb-6 relative z-10">
                      <h3 className="text-sm font-semibold text-dark-900 dark:text-white mb-3">Key Recommendations</h3>
                      <div className="space-y-3">
                        {result.recommendations.slice(0, 3).map((rec, i) => (
                          <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-dark-50 dark:bg-dark-800/50 border border-dark-100 dark:border-dark-700">
                            <span className="text-lg">{rec.icon}</span>
                            <div>
                              <p className="text-sm font-medium text-dark-900 dark:text-white">{rec.title}</p>
                              <p className="text-xs text-dark-500 mt-0.5">{rec.detail}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <button 
                    onClick={resetForm}
                    className="w-full btn-secondary mt-2 relative z-10"
                  >
                    <RefreshCw className="w-4 h-4" /> Start New Assessment
                  </button>

                  {/* Colored Glow Background based on risk */}
                  <div 
                    className="absolute top-0 right-0 w-64 h-64 rounded-full blur-[100px] pointer-events-none opacity-20 dark:opacity-10 z-0"
                    style={{ backgroundColor: result.risk_category.color }}
                  />
                </GlassCard>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full"
              >
                <GlassCard className="h-full flex flex-col items-center justify-center text-center p-12 min-h-[500px]">
                  <div className="w-24 h-24 mb-6 rounded-full bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center">
                    <Activity className="w-10 h-10 text-blue-500 opacity-50" />
                  </div>
                  <h3 className="text-xl font-semibold text-dark-900 dark:text-white mb-2">Awaiting Data</h3>
                  <p className="text-dark-500 text-sm max-w-xs">
                    Fill out the patient metrics and click Run ML Analysis to generate a comprehensive risk report.
                  </p>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default Predict;
