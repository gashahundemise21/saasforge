'use client';

import * as React from 'react';
import {
  BarChart,
  FolderOpen,
  CheckSquare,
  Users,
  Settings,
  CreditCard,
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
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function AppSidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  const navigation = [
    { name: 'Overview', href: '/dashboard', icon: BarChart },
    { name: 'Projects', href: '/dashboard/projects', icon: FolderOpen },
    { name: 'Tasks', href: '/dashboard/tasks', icon: CheckSquare },
    { name: 'Team Members', href: '/dashboard/members', icon: Users },
    { name: 'Billing', href: '/dashboard/billing', icon: CreditCard },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ];

  return (
    <Sidebar variant="inset">
      <SidebarHeader>
        <OrgSwitcher />
      </SidebarHeader>
      <SidebarContent>
        <SidebarMenu>
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <SidebarMenuItem key={item.name}>
                <SidebarMenuButton asChild isActive={isActive}>
                  <Link href={item.href}>
                    <item.icon />
                    <span>{item.name}</span>
                  </Link>
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
