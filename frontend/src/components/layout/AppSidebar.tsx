'use client';

import * as React from 'react';

/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable react-hooks/set-state-in-effect */
/* eslint-disable react-hooks/immutability */
import {
  BarChart,
  FolderOpen,
  CheckSquare,
  Users,
  Settings,
  CreditCard,
  Activity,
  Bell,
  Workflow,
} from 'lucide-react';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar';
import { OrgSwitcher } from '@/components/layout/OrgSwitcher';
import { GlobalSearch } from '@/components/layout/GlobalSearch';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { usePathname } from 'next/navigation';

export function AppSidebar() {
  const pathname = usePathname();
  const { logout, user, activeOrg } = useAuth();
  
  const [unreadCount, setUnreadCount] = React.useState(0);
  
  React.useEffect(() => {
    if (activeOrg) {
      api.get('/api/v1/notifications/unread-count')
        .then(res => setUnreadCount(res.data.unread_count))
        .catch(err => console.error('Failed to fetch unread count', err));
    }
  }, [activeOrg, pathname]);

  const navigation = [
    { name: 'Overview', href: '/dashboard', icon: BarChart },
    { name: 'Notifications', href: '/dashboard/notifications', icon: Bell },
    { name: 'Projects', href: '/dashboard/projects', icon: FolderOpen },
    { name: 'Tasks', href: '/dashboard/tasks', icon: CheckSquare },
    { name: 'Teams', href: '/dashboard/teams', icon: Users },
    { name: 'Activity', href: '/dashboard/activity', icon: Activity },
    { name: 'Team Members', href: '/dashboard/members', icon: Users },
    { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
    { name: 'Workflows', href: '/dashboard/workflows', icon: Workflow },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ];

  return (
    <Sidebar variant="inset">
      <SidebarHeader>
        <OrgSwitcher />
        <div className="px-2 py-2">
          <GlobalSearch />
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <SidebarMenuItem key={item.name}>
                <SidebarMenuButton render={<Link href={item.href} />} isActive={isActive}>
                    <item.icon />
                    <span className="flex-1">{item.name}</span>
                    {item.name === 'Notifications' && unreadCount > 0 && (
                      <Badge variant="destructive" className="ml-auto flex h-5 w-5 shrink-0 items-center justify-center rounded-full p-0 text-xs">
                        {unreadCount}
                      </Badge>
                    )}
                  </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton onClick={logout}>
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-muted">
                {user?.email?.charAt(0).toUpperCase()}
              </div>
              <div className="flex flex-col gap-1 leading-none">
                <span className="font-semibold">{user?.email}</span>
                <span className="text-xs text-muted-foreground">Log out</span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
