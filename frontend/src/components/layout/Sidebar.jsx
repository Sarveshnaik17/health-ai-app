import React from 'react';
import { NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LayoutDashboard, 
  Activity, 
  BarChart3, 
  FileText, 
  ChevronLeft,
  ChevronRight,
  LogOut,
  Hospital
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ isOpen, setIsOpen }) => {
  const { user, logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Predict Risk', path: '/predict', icon: Activity },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  return (
    <motion.div 
      initial={false}
      animate={{ width: isOpen ? 280 : 80 }}
      className="h-full glass-panel rounded-none border-y-0 border-l-0 z-20 flex flex-col shrink-0"
    >
      {/* Logo Area */}
      <div className="h-20 flex items-center justify-between px-6 border-b border-dark-200 dark:border-dark-800">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shrink-0 shadow-lg shadow-blue-500/20">
            <Hospital className="w-6 h-6 text-white" />
          </div>
          <AnimatePresence>
            {isOpen && (
              <motion.span 
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="font-bold text-xl bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent whitespace-nowrap"
              >
                MediVision AI
              </motion.span>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Toggle Button (Mobile & Desktop) */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-4 top-24 bg-white dark:bg-dark-800 border border-dark-200 dark:border-dark-700 rounded-full p-1.5 text-dark-500 hover:text-blue-500 transition-colors z-30 shadow-md hidden md:block"
      >
        {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-4 px-3 py-3 rounded-xl transition-all duration-200 group
              ${isActive 
                ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 font-medium' 
                : 'text-dark-600 dark:text-dark-400 hover:bg-dark-50 dark:hover:bg-dark-800 hover:text-dark-900 dark:hover:text-white'}
            `}
          >
            <item.icon className="w-5 h-5 shrink-0" />
            <AnimatePresence>
              {isOpen && (
                <motion.span 
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="whitespace-nowrap overflow-hidden"
                >
                  {item.name}
                </motion.span>
              )}
            </AnimatePresence>
            
            {/* Tooltip for collapsed state */}
            {!isOpen && (
              <div className="absolute left-16 px-2 py-1 bg-dark-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                {item.name}
              </div>
            )}
          </NavLink>
        ))}
      </div>

      {/* User Profile & Logout */}
      <div className="p-4 border-t border-dark-200 dark:border-dark-800">
        <div className={`flex items-center gap-3 px-3 py-3 rounded-xl ${isOpen ? 'bg-dark-50 dark:bg-dark-800/50' : ''}`}>
          <div 
            className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold shrink-0 shadow-sm"
            style={{ backgroundColor: user?.avatar_color || '#3b82f6' }}
          >
            {user?.full_name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          
          <AnimatePresence>
            {isOpen && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0 overflow-hidden"
              >
                <div className="truncate text-sm font-medium text-dark-900 dark:text-white">
                  {user?.full_name || user?.username}
                </div>
                <div className="truncate text-xs text-dark-500 dark:text-dark-400 capitalize">
                  {user?.role}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {isOpen && (
            <button 
              onClick={logout}
              className="p-2 text-dark-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors shrink-0"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
        
        {!isOpen && (
          <button 
            onClick={logout}
            className="mt-2 w-full flex items-center justify-center p-3 text-dark-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-colors group relative"
          >
            <LogOut className="w-5 h-5" />
            <div className="absolute left-16 px-2 py-1 bg-dark-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
              Logout
            </div>
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default Sidebar;
