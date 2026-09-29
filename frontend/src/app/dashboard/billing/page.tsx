'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ExternalLink } from 'lucide-react';

export default function BillingPage() {
  const { activeOrg } = useAuth();
  const [sub, setSub] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);

  useEffect(() => {
    if (activeOrg) {
      fetchSubscription();
    }
  }, [activeOrg]);

  const fetchSubscription = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/v1/billing/subscription');
      setSub(res.data);
    } catch (err) {
      console.error('Failed to fetch subscription', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPortal = async () => {
    setPortalLoading(true);
    try {
      const res = await api.post('/api/v1/billing/portal');
      // Redirect to Stripe
      window.location.href = res.data.url;
    } catch (err) {
      console.error('Failed to generate portal session', err);
    } finally {
      setPortalLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription and billing details for {activeOrg?.name}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>
              You are currently on the <strong className="capitalize">{activeOrg?.plan_id}</strong> plan.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm font-medium">Status</span>
              {sub?.status ? (
                <Badge variant={sub.status === 'active' ? 'default' : 'secondary'} className="capitalize">
                  {sub.status}
                </Badge>
              ) : (
                <Badge variant="outline">Free / No Subscription</Badge>
              )}
            </div>
            {sub?.current_period_end && (
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm font-medium">Renewal Date</span>
                <span className="text-sm text-muted-foreground">
                  {new Date(sub.current_period_end * 1000).toLocaleDateString()}
                </span>
              </div>
            )}
            
            <div className="bg-muted p-4 rounded-lg mt-4 text-sm text-muted-foreground">
              Your plan dictates your API quotas. The Free plan limits you to 1 project and 1 member. Pro and Enterprise unlock unlimited projects, team members, and priority webhooks.
            </div>
          </CardContent>
          <CardFooter>
            <Button onClick={handleOpenPortal} disabled={portalLoading} className="w-full sm:w-auto">
              <ExternalLink className="mr-2 h-4 w-4" />
              {portalLoading ? 'Loading Portal...' : 'Manage Billing in Stripe'}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}
