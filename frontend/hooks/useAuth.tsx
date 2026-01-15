'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/services/api';

// Hardcoded production URL for Vercel deployment - same as api.ts
const PRODUCTION_API_URL = 'https://ai-data-analyst-api.onrender.com';

const getApiBaseUrl = () => {
  // Use hardcoded production URL on Vercel
  if (process.env.VERCEL === '1') {
    return PRODUCTION_API_URL;
  }
  // Use environment variable for other environments
  return process.env.NEXT_PUBLIC_API_URL || PRODUCTION_API_URL;
};

const API_BASE_URL = getApiBaseUrl();

// Debug log
console.log('🔐 Auth API Base URL:', API_BASE_URL);

interface User {
  id: number;
  email: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authApi.login(email, password);
    const { access_token } = res;
    localStorage.setItem('token', access_token);

    // Fetch user info from /me endpoint
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${access_token}`,
        },
      });
      const userInfo = await response.json();

      localStorage.setItem('user', JSON.stringify(userInfo));
      setToken(access_token);
      setUser(userInfo);
      router.push('/dashboard');
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      // Fallback to basic info
      localStorage.setItem('user', JSON.stringify({ id: 1, email }));
      setToken(access_token);
      setUser({ id: 1, email });
      router.push('/dashboard');
    }
  };

  const register = async (email: string, password: string) => {
    await authApi.register(email, password);
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

