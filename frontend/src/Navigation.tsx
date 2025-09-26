import { useDispatch, useSelector } from 'react-redux'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { logoutRecord } from './store/accountSlice'
import type { AppDispatch, RootState } from './store/store'
import './Navigation.css'

function Navigation() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate() // Now this works!
  const { account } = useSelector((state: RootState) => state.account)

  const handleLogout = () => {
    dispatch(logoutRecord())
      .then(() => navigate('/login'))
  }

  const loggedInNav = (
    <>
      <Link to="home">Home</Link>
      <button onClick={handleLogout} className="nav-logout-btn">
        Logout
      </button>
    </>
  )
  const loggedOutNav = (
    <>
      <Link to="register">Register</Link>
      <Link to="login">Log In</Link>
    </>
  )

  return <nav>{account ? loggedInNav : loggedOutNav}</nav>
}

export default Navigation