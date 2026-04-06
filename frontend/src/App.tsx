import { Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import ResumeManager from './components/ResumeManager'
import JobManager from './components/JobManager'
import MatchingInterface from './components/MatchingInterface'
import Layout from './components/Layout'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/resumes" element={<ResumeManager />} />
          <Route path="/jobs" element={<JobManager />} />
          <Route path="/matching" element={<MatchingInterface />} />
        </Routes>
      </Layout>
    </div>
  )
}

export default App
