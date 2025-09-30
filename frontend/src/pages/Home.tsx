import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { accountRecord } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'
import './../styles/Home.css'

function Home() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate();
  const { account, error, loading } = useSelector((state: RootState) => state.account)

  useEffect(() => {
    const loadAccount = async () => {
      try {
        await dispatch(accountRecord()).unwrap()
      } catch (error) {
        navigate('/login')
      }
    }
    
    loadAccount()
  }, [dispatch, navigate])

  if (!account) {
    return null;
  }
  
  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="welcome-message">Hello {account.firstName}, welcome back!</h1>
      </div>
    </div>
  )
}

export default Home