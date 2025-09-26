import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Register from './pages/Register.tsx'
import Login from './pages/Login.tsx'
import Home from './pages/Home.tsx'
import Navigation from './Navigation.tsx'
import './App.css'

function App() {
  return (
    <Router>
      <header>
        <Navigation />
      </header>
      <main>
        <Routes>
          <Route path="/" element={<div>Root page</div>} />
          <Route path="register" element={<Register />} />
          <Route path="login" element={<Login />} />
          <Route path="home" element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
    </Router>
  )
}

export default App
