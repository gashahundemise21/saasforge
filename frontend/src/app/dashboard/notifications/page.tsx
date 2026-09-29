'use client';

import { useState, useEffect } from 'react';

 
 
 
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { format } from 'date-fns';
import { Loader2, Bell, Check, CheckCircle2, Circle } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function NotificationsPage() {
  const { activeOrg } = useAuth();
  const router = useRouter();
  
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [marking, setMarking] = useState<string | null>(null);
  
  useEffect(() => {
    if (activeOrg) {
      fetchNotifications();
    }
  }, [activeOrg]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/v1/notifications');
      setNotifications(res.data);
    } catch (err) {
      console.error('Failed to fetch notifications', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id: string, e?: React.MouseEvent) => {
    if (e) {
      e.stopPropagation();
      e.preventDefault();
    }
    try {
      setMarking(id);
      await api.put(`/api/v1/notifications/${id}/read`);
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, read_at: new Date().toISOString() } : n
      ));
    } catch (err) {
      console.error('Failed to mark as read', err);
    } finally {
      setMarking(null);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      setMarking('all');
      await api.put('/api/v1/notifications/read-all');
      setNotifications(notifications.map(n => 
        !n.read_at ? { ...n, read_at: new Date().toISOString() } : n
      ));
    } catch (err) {
      console.error('Failed to mark all as read', err);
    } finally {
      setMarking(null);
    }
  };

  const handleNotificationClick = (notification: any) => {
    if (!notification.read_at) {
      handleMarkAsRead(notification.id);
    }
    if (notification.action_url) {
      router.push(notification.action_url);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.read_at).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
          <p className="text-muted-foreground mt-1">
            You have {unreadCount} unread message{unreadCount !== 1 ? 's' : ''}.
          </p>
        </div>
        
        {unreadCount > 0 && (
          <Button 
            variant="outline" 
            onClick={handleMarkAllAsRead}
            disabled={marking === 'all'}
          >
            {marking === 'all' ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Check className="h-4 w-4 mr-2" />
            )}
            Mark all as read
          </Button>
        )}
      </div>

      <div className="space-y-4">
        {notifications.length === 0 ? (
          <div className="text-center py-12 bg-muted/30 rounded-lg border border-dashed">
            <Bell className="h-8 w-8 mx-auto text-muted-foreground mb-3" />
            <h3 className="text-lg font-medium">All caught up!</h3>
            <p className="text-muted-foreground">You don't have any notifications right now.</p>
          </div>
        ) : (
          notifications.map((notif) => (
            <Card 
              key={notif.id} 
              className={`overflow-hidden transition-colors group ${!notif.read_at ? 'bg-muted/30' : ''} ${notif.action_url ? 'cursor-pointer hover:bg-muted/50' : ''}`}
              onClick={() => handleNotificationClick(notif)}
            >
              <CardContent className="p-4 sm:p-6 flex items-start gap-4">
                <div className="mt-1">
                  {!notif.read_at ? (
                    <Circle className="h-3 w-3 fill-primary text-primary" />
                  ) : (
                    <CheckCircle2 className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className={`text-sm font-medium ${!notif.read_at ? 'text-foreground' : 'text-muted-foreground'}`}>
                      {notif.title}
                    </p>
                    <span className="text-xs text-muted-foreground whitespace-nowrap ml-4">
                      {format(new Date(notif.created_at), 'MMM d, h:mm a')}
                    </span>
                  </div>
                  <p className={`text-sm ${!notif.read_at ? 'text-foreground/90' : 'text-muted-foreground'}`}>
                    {notif.message}
                  </p>
                </div>
                
                {!notif.read_at && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="opacity-0 group-hover:opacity-100 transition-opacity h-8 text-xs"
                    onClick={(e) => handleMarkAsRead(notif.id, e)}
                    disabled={marking === notif.id}
                  >
                    {marking === notif.id ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      'Mark read'
                    )}
                  </Button>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
