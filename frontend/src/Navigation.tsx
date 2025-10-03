import { useDispatch, useSelector } from 'react-redux'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { logoutRecord } from './store/accountSlice'
import type { AppDispatch, RootState } from './store/store'
import './styles/Navigation.css'

function Navigation() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate() // Now this works!
  const { account } = useSelector((state: RootState) => state.account)

  const handleLogout = () => {
    dispatch(logoutRecord())
      .then(() => {
        // Clear chat widget state on logout
        window.dispatchEvent(new CustomEvent('user-logout'));
        navigate('/login');
      })
  }

  const loggedInNav = (
    <>
      <Link to="/" className="nav-link">Movies</Link>
      <Link to="/my-movies" className="nav-link">My Movies</Link>
      <Link to="/home" className="nav-link">Home</Link>
      <button onClick={handleLogout} className="nav-logout-btn">
        Logout
      </button>
    </>
  )
  const loggedOutNav = (
    <>
      <Link to="/" className="nav-link">Movies</Link>
      <Link to="/register" className="nav-link">Register</Link>
      <Link to="/login" className="nav-link">Log In</Link>
    </>
  )

  return <nav>{account ? loggedInNav : loggedOutNav}</nav>
}

export default Navigation