import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'
import { accountRecord } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'

interface ProtectedRouteProps {
  children: React.ReactNode
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  const dispatch = useDispatch<AppDispatch>()
  const { account, loading } = useSelector((state: RootState) => state.account)
  const [authChecked, setAuthChecked] = useState(false)

  useEffect(() => {
    if (!account && !authChecked && !loading) {
      setAuthChecked(true)
      dispatch(accountRecord())
    } else if (account && !authChecked) {
      setAuthChecked(true)
    }
  }, [dispatch, account, authChecked, loading])

  // Still checking auth
  if (!authChecked && loading) {
    return <div>Loading...</div>
  }

  // Auth check complete, but no account - redirect
  if (authChecked && !account) {
    return <Navigate to="/login" replace />
  }

  // User is authenticated or still loading initial check
  if (account) {
    return <>{children}</>
  }

  return <div>Loading...</div>
}

export default ProtectedRoute