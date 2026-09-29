'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

export default function DashboardPage() {
  const { user, activeOrg, logout } = useAuth();

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      
      <div className="rounded-lg border p-6 bg-card text-card-foreground shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Welcome back!</h2>
        <div className="space-y-2 text-sm">
          <p><span className="font-medium">User ID:</span> {user?.id}</p>
          <p><span className="font-medium">Email:</span> {user?.email}</p>
          <p><span className="font-medium">Active Org:</span> {activeOrg?.name} ({activeOrg?.slug})</p>
        </div>
        
        <Button variant="outline" className="mt-6" onClick={logout}>
          Log out
        </Button>
      </div>
    </div>
  );
}
