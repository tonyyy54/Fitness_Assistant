import { Navigate, Route, Routes } from 'react-router-dom'

import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import PlanPage from './pages/PlanPage'
import ProfilePage from './pages/ProfilePage'
import RegisterPage from './pages/RegisterPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/plan" element={<PlanPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
