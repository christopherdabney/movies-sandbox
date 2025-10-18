import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Register from './pages/Register.tsx'
import Login from './pages/Login.tsx'
import Home from './pages/Home.tsx'
import Movies from './pages/Movies.tsx'
import MyMovies from './pages/MyMovies.tsx'
import MovieDetail from './pages/MovieDetail.tsx'
import Navigation from './Navigation.tsx'
import ChatWidget from './components/ChatWidget'
import VerifyEmail from './pages/VerifyEmail';

import { useEffect } from 'react'
import { useDispatch } from 'react-redux'
import { accountRecord } from './store/accountSlice'

import type { AppDispatch } from './store/store'

import './styles/App.css'

function App() {
  const dispatch = useDispatch<AppDispatch>()

  useEffect(() => {
    // Try to restore session from cookie on app load
    dispatch(accountRecord())
  }, [dispatch])

  return (
    <Router>
      <header>
        <Navigation />
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Movies />} />
          <Route path="/movies/:id" element={<MovieDetail />} />
          <Route path="register" element={<Register />} />
          <Route path="login" element={<Login />} />
          <Route path="/verify-email/:token" element={<VerifyEmail />} />
          <Route path="home" element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          } />
          <Route path="/my-movies" element={
            <ProtectedRoute>
              <MyMovies />
            </ProtectedRoute>
          } />
        </Routes>
      </main>
      <ChatWidget />
    </Router>
  )
}

export default App
