import React, { useContext } from 'react';
import { Menu, Bell, Sun, Moon, Search } from 'lucide-react';
import { ThemeContext } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';

const Navbar = ({ toggleSidebar, isSidebarOpen }) => {
  const { theme, toggleTheme } = useContext(ThemeContext);
  const { user } = useAuth();

  return (
    <header className="h-20 glass-panel rounded-none border-x-0 border-t-0 z-10 flex items-center justify-between px-6 shrink-0 sticky top-0">
      <div className="flex items-center gap-4">
        {/* Mobile menu toggle */}
        <button 
          onClick={toggleSidebar}
          className="md:hidden p-2 text-dark-600 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-800 rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search */}
        <div className="hidden md:flex items-center relative group">
          <Search className="w-4 h-4 text-dark-400 absolute left-3 group-focus-within:text-blue-500 transition-colors" />
          <input 
            type="text" 
            placeholder="Search insights, patients..." 
            className="bg-dark-50 dark:bg-dark-900 border border-dark-200 dark:border-dark-700 text-dark-900 dark:text-white rounded-full pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 w-64 focus:w-80 transition-all duration-300"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Theme Toggle */}
        <button 
          onClick={toggleTheme}
          className="p-2.5 text-dark-600 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-800 rounded-full transition-colors relative group"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        {/* Notifications */}
        <button className="p-2.5 text-dark-600 dark:text-dark-300 hover:bg-dark-100 dark:hover:bg-dark-800 rounded-full transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full border border-white dark:border-dark-900"></span>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
