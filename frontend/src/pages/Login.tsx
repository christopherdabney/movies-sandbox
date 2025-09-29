import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { loginRecord, clearError } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'

import './../styles/Login.css'

function Login() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate();
  const { loading, error } = useSelector((state: RootState) => state.account)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  useEffect(() => {
      dispatch(clearError());
  }, [dispatch]);

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await dispatch(loginRecord({
        email: formData.email,
        password: formData.password
      })).unwrap()
      navigate('/home', { replace: true })
    } catch (err) {
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">Welcome Back</h1>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInput}
              className="form-input"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInput}
              className="form-input"
              required
            />
          </div>

          <button type="submit" className="submit-button">
            Sign In
          </button>
          {error && <div className="error-message">{error}</div>}
        </form>

        <p className="signup-link">
          Don't have an account?
          <Link className="signup-link-text" to="/register"> Create one</Link>
        </p>
      </div>
    </div>
  );
}

export default Login