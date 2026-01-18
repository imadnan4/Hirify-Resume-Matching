import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Dashboard from './components/Dashboard'
import ResumeManager from './components/ResumeManager'
import JobManager from './components/JobManager'
import MatchingInterface from './components/MatchingInterface'
import Layout from './components/Layout'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Layout>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/resumes" element={<ResumeManager />} />
            <Route path="/jobs" element={<JobManager />} />
            <Route path="/matching" element={<MatchingInterface />} />
          
          </Routes>
        </motion.div>
      </Layout>
    </div>
  )
}

export default App
