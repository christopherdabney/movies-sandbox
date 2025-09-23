import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Register from './pages/Register.tsx'
import Login from './pages/Login.tsx'
import Home from './pages/Home.tsx'
import './App.css'

function App() {
  return (
    <Router>
      <header>
        <nav>
          <Link to="register">
            Register
          </Link>
          <Link to="login">
            Log In
          </Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<div>Root page</div>} />
          <Route path="register" element={<Register />} />
          <Route path="login" element={<Login />} />
          <Route path="home" element={<Home />} />
        </Routes>
      </main>
    </Router>
  )
}

export default App
