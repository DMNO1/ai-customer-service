import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import KnowledgeBase from './pages/KnowledgeBase'
import Conversations from './pages/Conversations'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import HealthStatus from './pages/HealthStatus'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/knowledge-base" element={<KnowledgeBase />} />
        <Route path="/conversations" element={<Conversations />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/health" element={<HealthStatus />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App
