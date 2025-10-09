import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { registerRecord, clearError } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'
import './../styles/Register.css'

function Register() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate();
  const { loading, error } = useSelector((state: RootState) => state.account)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    birthMonth: '',
    birthDay: '',
    birthYear: ''
  })

  useEffect(() => {
      dispatch(clearError());
  }, [dispatch]);

  const handleInput = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const dateOfBirth = `${formData.birthYear}-${formData.birthMonth}-${formData.birthDay}`;
    try {
      await dispatch(registerRecord({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        dateOfBirth: dateOfBirth
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

          <div className="form-group-row">
            <div className="form-group-third">
              <label className="form-label">Birth Month</label>
              <select
                name="birthMonth"
                value={formData.birthMonth}
                onChange={handleInput}
                className="form-select"
                required
              >
                <option value="">Month</option>
                <option value="01">January</option>
                <option value="02">February</option>
                <option value="03">March</option>
                <option value="04">April</option>
                <option value="05">May</option>
                <option value="06">June</option>
                <option value="07">July</option>
                <option value="08">August</option>
                <option value="09">September</option>
                <option value="10">October</option>
                <option value="11">November</option>
                <option value="12">December</option>
              </select>
            </div>
            
            <div className="form-group-third">
              <label className="form-label">Day</label>
              <select
                name="birthDay"
                value={formData.birthDay}
                onChange={handleInput}
                className="form-select"
                required
              >
                <option value="">Day</option>
                {Array.from({length: 31}, (_, i) => i + 1).map(day => (
                  <option key={day} value={day.toString().padStart(2, '0')}>
                    {day}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group-third">
              <label className="form-label">Year</label>
              <select
                name="birthYear"
                value={formData.birthYear}
                onChange={handleInput}
                className="form-select"
                required
              >
                <option value="">Year</option>
                {Array.from({length: 125}, (_, i) => new Date().getFullYear() - i).map(year => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
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