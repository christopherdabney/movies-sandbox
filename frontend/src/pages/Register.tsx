import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { registerRecord } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'

import './Register.css'

function Register() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate();
  const { loading, error } = useSelector((state: RootState) => state.account)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
  })

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
      await dispatch(registerRecord({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName
      })).unwrap()
      navigate('/home', { replace: true })
    } catch (err) {
    }
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <h1 className="register-title">Create Account</h1>
        
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

          <div className="form-group-row">
            <div className="form-group-half">
              <label className="form-label">First Name</label>
              <input
                type="text"
                name="firstName"
                value={formData.firstName}
                onChange={handleInput}
                className="form-input"
                required
              />
            </div>
            
            <div className="form-group-half">
              <label className="form-label">Last Name</label>
              <input
                type="text"
                name="lastName"
                value={formData.lastName}
                onChange={handleInput}
                className="form-input"
                required
              />
            </div>
          </div>

          <button type="submit" className="submit-button">
            Create Account
          </button>
          {error && <div className="error-message">{error}</div>}
        </form>

        <p className="signup-link">
          Already have an account?
          <Link className="signup-link-text" to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
}

export default Register