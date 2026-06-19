import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Briefcase, FileText, Home, Target } from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarSeparator,
  useSidebar,
} from '@/components/optics/sidebar.tsx'

interface NavigationItem {
  to: string
  label: string
  icon: React.ComponentType<any>
  badge?: string
}

const mainNavigation: NavigationItem[] = [
  { to: '/', label: 'Dashboard', icon: Home },
  { to: '/resumes', label: 'Resumes', icon: FileText },
  { to: '/jobs', label: 'Jobs', icon: Briefcase },
  { to: '/matching', label: 'Matching', icon: Target, badge: 'AI' },
]

export const AppSidebar: React.FC = () => {
  const location = useLocation()
  const { isMobile, setOpenMobile } = useSidebar()

  const closeOnMobile = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
  }

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-2.5 py-3">
        <Link
          to="/"
          onClick={closeOnMobile}
          className="grid min-w-0 px-2 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden"
        >
          <span className="truncate font-semibold">Hirify</span>
          <span className="truncate text-xs text-sidebar-foreground/70">Talent Matching OS</span>
        </Link>
      </SidebarHeader>

      <SidebarSeparator />

      <SidebarContent className="px-1.5 py-2">
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainNavigation.map((item) => {
                const Icon = item.icon

                return (
                  <SidebarMenuItem key={item.to}>
                    <SidebarMenuButton
                      asChild
                      isActive={location.pathname === item.to}
                      tooltip={item.label}
                    >
                      <Link to={item.to} onClick={closeOnMobile}>
                        <Icon />
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                    {item.badge ? <SidebarMenuBadge>{item.badge}</SidebarMenuBadge> : null}
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarSeparator />

      

    </Sidebar>
  )
}
