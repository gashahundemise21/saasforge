'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan_id: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  activeOrg: Organization | null;
  organizations: Organization[];
  isLoading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
  switchOrganization: (slug: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [activeOrg, setActiveOrg] = useState<Organization | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for token on mount
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchUserData();
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserData = async () => {
    try {
      // 1. Fetch user profile
      const userRes = await api.get('/api/v1/users/me');
      setUser(userRes.data);

      // 2. Fetch user's organizations
      const orgsRes = await api.get('/api/v1/organizations/me');
      const fetchedOrgs = orgsRes.data;
      setOrganizations(fetchedOrgs);

      // 3. Determine active org
      if (fetchedOrgs.length > 0) {
        const storedOrgSlug = localStorage.getItem('activeOrgSlug');
        let selectedOrg = fetchedOrgs.find((o: Organization) => o.slug === storedOrgSlug);
        
        if (!selectedOrg) {
          selectedOrg = fetchedOrgs[0];
          localStorage.setItem('activeOrgSlug', selectedOrg.slug);
        }
        setActiveOrg(selectedOrg);
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      // Let the axios interceptor handle 401s (it will clear localStorage)
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setIsLoading(true);
    await fetchUserData();
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('activeOrgSlug');
    setToken(null);
    setUser(null);
    setActiveOrg(null);
    setOrganizations([]);
    window.location.href = '/login';
  };

  const switchOrganization = (slug: string) => {
    const newOrg = organizations.find(o => o.slug === slug);
    if (newOrg) {
      localStorage.setItem('activeOrgSlug', slug);
      setActiveOrg(newOrg);
      // Reload to ensure all data is fetched with the new org context
      window.location.href = '/dashboard';
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        activeOrg,
        organizations,
        isLoading,
        login,
        logout,
        switchOrganization,
      }}
    >
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
