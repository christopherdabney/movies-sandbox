import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import './Home.css'

function Home() {
  const navigate = useNavigate();
  const { account } = useSelector((state: RootState) => state.account)

  useEffect(() => {
    if (!account) {
        navigate('/login', { replace: true })
    }
  }, [account,]);

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