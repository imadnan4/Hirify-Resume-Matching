import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import ResumeManager from './components/ResumeManager'
import JobManager from './components/JobManager'
import MatchingInterface from './components/MatchingInterface'
import Layout from './components/Layout'
import Login from './components/Login'
import { useAuth } from './lib/AuthContext'

function App() {
  const { status } = useAuth()

  if (status === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <p className="text-sm text-muted-foreground">Loading…</p>
      </div>
    )
  }

  if (status === 'unauthenticated') {
    return <Login />
  }

  return (
    <div className="min-h-screen bg-background">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/resumes" element={<ResumeManager />} />
          <Route path="/jobs" element={<JobManager />} />
          <Route path="/matching" element={<MatchingInterface />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </div>
  )
}

export default App
