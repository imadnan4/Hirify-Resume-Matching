import React, { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/optics/sidebar.tsx'
import { AppSidebar } from './AppSidebar'
import { ToastProvider } from './ui/toast'

interface LayoutProps {
  children: ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()

  return (
    <ToastProvider>
      <SidebarProvider defaultOpen>
        <AppSidebar />

        <SidebarInset className="min-w-0 overflow-x-hidden">
          <main className="w-full min-w-0 overflow-x-hidden px-4 py-4 md:px-6 md:py-6 lg:px-8">
            <div className="mb-2 flex md:hidden">
              <SidebarTrigger />
            </div>
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="mx-auto w-full min-w-0 max-w-7xl"
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

