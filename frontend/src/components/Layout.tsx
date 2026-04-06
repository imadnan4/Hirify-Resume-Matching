import React, { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FileText, Briefcase, Target, Home } from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
} from '@/components/optics/sidebar'
import { ToastProvider } from './ui/toast'

interface LayoutProps {
  children: ReactNode
}

interface NavItem {
  to: string
  icon: React.ComponentType<any>
  label: string
  badge?: string
}

const navItems: NavItem[] = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/resumes', icon: FileText, label: 'Resumes' },
  { to: '/jobs', icon: Briefcase, label: 'Jobs' },
  { to: '/matching', icon: Target, label: 'Matching' },
]

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <ToastProvider>
      <SidebarProvider defaultOpen>
        <Sidebar collapsible="icon">
          <SidebarHeader>
            <div className="flex items-center justify-between gap-2 px-2 py-2 group-data-[collapsible=icon]:justify-center">
              <div className="flex items-center gap-2 group-data-[collapsible=icon]:gap-0">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white">
                  <FileText className="h-4 w-4" />
                </div>
                <div className="flex flex-col leading-none group-data-[collapsible=icon]:hidden">
                  <span className="font-semibold">Hirify</span>
                  <span className="text-xs text-muted-foreground">Resume matching</span>
                </div>
              </div>
              <SidebarTrigger className="hidden md:inline-flex" />
            </div>
          </SidebarHeader>

          <SidebarContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const Icon = item.icon
                return (
                  <SidebarMenuItem key={item.to}>
                    <SidebarMenuButton
                      isActive={isActive(item.to)}
                      tooltip={item.label}
                      render={<Link to={item.to} />}
                    >
                      <Icon />
                      <span>{item.label}</span>
                      {item.badge ? <SidebarMenuBadge>{item.badge}</SidebarMenuBadge> : null}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarContent>

          <SidebarRail />
        </Sidebar>

        <SidebarInset>
          <main className="px-4 py-4 md:px-6 md:py-6 lg:px-8">
            <div className="mb-2 flex md:hidden">
              <SidebarTrigger />
            </div>
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="mx-auto w-full max-w-7xl"
            >
              {children}
            </motion.div>
          </main>
        </SidebarInset>
      </SidebarProvider>
    </ToastProvider>
  )
}

export default Layout

