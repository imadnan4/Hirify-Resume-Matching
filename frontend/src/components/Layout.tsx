import React, { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, FileText, Briefcase, Target, Home, ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
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
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <ToastProvider>
      <div className="min-h-screen bg-gray-50">
        {/* Sidebar */}
        <motion.aside
          className={cn(
            'fixed inset-y-0 left-0 z-50 bg-white border-r border-gray-200 transition-all duration-300 hidden md:block',
            isSidebarCollapsed ? 'w-16' : 'w-64'
          )}
          initial={{ x: -100 }}
          animate={{ x: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Sidebar Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <motion.div 
              className="flex items-center space-x-2"
              animate={{ opacity: isSidebarCollapsed ? 0 : 1 }}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white">
                <FileText className="h-4 w-4" />
              </div>
              {!isSidebarCollapsed && (
                <span className="text-xl font-bold text-gray-900">Hirify</span>
              )}
            </motion.div>
            
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              className="h-8 w-8"
            >
              {isSidebarCollapsed ? 
                <ChevronRight className="h-4 w-4" /> : 
                <ChevronLeft className="h-4 w-4" />
              }
            </Button>
          </div>

          {/* Sidebar Navigation */}
          <nav className="p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <Link key={item.to} to={item.to}>
                  <motion.div
                    className={cn(
                      'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors group',
                      isActive(item.to)
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    )}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Icon className={cn('h-5 w-5 flex-shrink-0', isSidebarCollapsed ? 'mx-auto' : 'mr-3')} />
                    {!isSidebarCollapsed && (
                      <>
                        <span>{item.label}</span>
                        {item.badge && (
                          <Badge variant="secondary" className="ml-auto">
                            {item.badge}
                          </Badge>
                        )}
                      </>
                    )}
                  </motion.div>
                </Link>
              )
            })}
          </nav>

          {/* Sidebar Footer */}
          <div className="absolute bottom-0 left-0 right-0 p-4 border-t">
            
          </div>
        </motion.aside>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {isMobileMenuOpen && (
            <>
              <motion.div
                className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsMobileMenuOpen(false)}
              />
              <motion.aside
                className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 md:hidden"
                initial={{ x: -256 }}
                animate={{ x: 0 }}
                exit={{ x: -256 }}
                transition={{ duration: 0.3 }}
              >
                {/* Mobile Header */}
                <div className="flex items-center justify-between p-4 border-b">
                  <div className="flex items-center space-x-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white">
                      <FileText className="h-4 w-4" />
                    </div>
                    <span className="text-xl font-bold text-gray-900">Hirify</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                {/* Mobile Navigation */}
                <nav className="p-4 space-y-2">
                  {navItems.map((item) => {
                    const Icon = item.icon
                    return (
                      <Link key={item.to} to={item.to} onClick={() => setIsMobileMenuOpen(false)}>
                        <motion.div
                          className={cn(
                            'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                            isActive(item.to)
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-700 hover:bg-gray-100'
                          )}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <Icon className="h-5 w-5 mr-3" />
                          <span>{item.label}</span>
                          {item.badge && (
                            <Badge variant="secondary" className="ml-auto">
                              {item.badge}
                            </Badge>
                          )}
                        </motion.div>
                      </Link>
                    )
                  })}
                </nav>
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className={cn('transition-all duration-300', isSidebarCollapsed ? 'md:ml-16' : 'md:ml-64')}>
          {/* Top Header */}
          <header className="bg-white border-b border-gray-200 px-4 py-3">
            <div className="flex items-center justify-between">
              {/* Mobile menu button */}
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={() => setIsMobileMenuOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>

              {/* Page Title */}
              <div className="flex-1 md:ml-0 ml-4">
                <h1 className="text-xl font-semibold text-gray-900">
                  {navItems.find(item => item.to === location.pathname)?.label || 'Dashboard'}
                </h1>
              </div>

              {/* Right side actions */}
              <div className="flex items-center space-x-3">
                {/* Notifications */}
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="p-6">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </main>
        </div>
      </div>
    </ToastProvider>
  )
}

export default Layout

