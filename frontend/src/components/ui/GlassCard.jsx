import React from 'react';
import { motion } from 'framer-motion';

const GlassCard = ({ children, className = '', hover = true, delay = 0, padding = 'p-6' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`glass-panel ${padding} ${hover ? 'hover:-translate-y-1' : ''} ${className}`}
    >
      {children}
    </motion.div>
  );
};

export default GlassCard;
