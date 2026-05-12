import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../utils/api';

export const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const storedUser = localStorage.getItem('user');
          if (storedUser) {
            setUser(JSON.parse(storedUser));
          } else {
            // Fetch profile if we have token but no user object
            const res = await api.get('/auth/profile');
            if (res.data.status === 'success') {
              setUser(res.data.data);
              localStorage.setItem('user', JSON.stringify(res.data.data));
            }
          }
        } catch (error) {
          console.error("Auth init failed:", error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password });
    if (res.data.status === 'success') {
      const { token, user: userData } = res.data.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    }
    return { success: false, error: res.data.error || 'Login failed' };
  };

  const register = async (username, password, full_name) => {
    const res = await api.post('/auth/register', { username, password, full_name });
    if (res.data.status === 'success') {
      const { token, user: userData } = res.data.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    }
    return { success: false, error: res.data.error || 'Registration failed' };
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const updateProfile = async (data) => {
    const res = await api.put('/auth/profile', data);
    if (res.data.status === 'success') {
       // Refresh profile
       const profileRes = await api.get('/auth/profile');
       if (profileRes.data.status === 'success') {
          setUser(profileRes.data.data);
          localStorage.setItem('user', JSON.stringify(profileRes.data.data));
       }
       return { success: true };
    }
    return { success: false, error: res.data.error || 'Update failed' };
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
};
