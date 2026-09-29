'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { format } from 'date-fns';
import { Loader2, Activity } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

 
 

export default function ActivityFeedPage() {
  const { activeOrg } = useAuth();
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (activeOrg) {
      fetchActivity();
    }
  }, [activeOrg]);

  const fetchActivity = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.get('/api/v1/audit-logs');
      setActivities(res.data);
    } catch (err: any) {
      console.error('Failed to fetch activity', err);
      if (err.response?.status === 403) {
        setError("You don't have permission to view organization activity.");
      } else {
        setError("Failed to load activity feed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const formatAction = (action: string) => {
    return action.replace(/\./g, ' ').replace(/_/g, ' ');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Activity Feed</h1>
        <p className="text-muted-foreground">
          Recent actions and events within your organization
        </p>
      </div>

      {error ? (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive text-center">{error}</p>
          </CardContent>
        </Card>
      ) : activities.length === 0 ? (
        <Card>
          <CardContent className="pt-6 flex flex-col items-center justify-center text-center py-12">
            <Activity className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
            <h3 className="text-lg font-medium">No activity yet</h3>
            <p className="text-muted-foreground">When team members take actions, they will appear here.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {activities.map((activity) => (
            <Card key={activity.id}>
              <CardContent className="p-4 sm:p-6 flex items-start gap-4">
                <Avatar className="h-10 w-10 mt-1">
                  <AvatarFallback className="bg-primary/10 text-primary">
                    <Activity className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium capitalize">
                      {formatAction(activity.action)}
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {format(new Date(activity.created_at), 'MMM d, h:mm a')}
                    </span>
                  </div>
                  
                  <div className="text-sm text-muted-foreground flex items-center gap-2 flex-wrap">
                    <span>
                      Actor: {activity.actor_type === 'user' ? 'User' : 'System'} ({activity.actor_id.substring(0, 8)}...)
                    </span>
                    <span>•</span>
                    <span>
                      Resource: <Badge variant="outline" className="capitalize">{activity.resource_type}</Badge>
                    </span>
                    {activity.ip_address && (
                      <>
                        <span>•</span>
                        <span className="text-xs">{activity.ip_address}</span>
                      </>
                    )}
                  </div>
                  
                  {activity.details && Object.keys(activity.details).length > 0 && (
                    <div className="mt-2 text-xs bg-muted p-2 rounded-md overflow-x-auto">
                      <pre>{JSON.stringify(activity.details, null, 2)}</pre>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
