import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { accountRecord } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'
import { API_ENDPOINTS } from '../constants/api'
import { WatchlistFilterValue } from '../types/Watchlist';
import type { WatchlistFilter } from '../types/Watchlist';
import './../styles/Home.css'

interface WatchlistStats {
  total: number;
  toWatch: number;
  watched: number;
  watching: number;
}

function Home() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate();
  const { account, error, loading } = useSelector((state: RootState) => state.account)
  const [stats, setStats] = useState<WatchlistStats>({
    total: 0,
    toWatch: 0,
    watched: 0
  });
  const [statsLoading, setStatsLoading] = useState(true);

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

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setStatsLoading(true);
        
        // Fetch all watchlist items
        const allResponse = await fetch(API_ENDPOINTS.WATCHLIST.LIST, {
          credentials: 'include',
        });
        const allData = await allResponse.json();
        
        // Fetch queued items
        const toWatchResponse = await fetch(`${API_ENDPOINTS.WATCHLIST.LIST}?status=${WatchlistFilterValue.QUEUED}`, {
          credentials: 'include',
        });
        const toWatchData = await toWatchResponse.json();
        
        // Fetch watched items
        const watchedResponse = await fetch(`${API_ENDPOINTS.WATCHLIST.LIST}?status=${WatchlistFilterValue.WATCHED}`, {
          credentials: 'include',
        });
        const watchedData = await watchedResponse.json();

        setStats({
          total: allData.count || 0,
          toWatch: toWatchData.count || 0,
          watched: watchedData.count || 0,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setStatsLoading(false);
      }
    };
    
    if (account) {
      fetchStats();
    }
  }, [account]);

  if (!account) {
    return null;
  }
  
  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="welcome-message">
          {account.firstName} {account.lastName}
        </h1>

        <div>
          Age: {account.age}
        </div>
        
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-number">{stats.total}</div>
            <div className="stat-label">Total Movies</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.toWatch}</div>
            <div className="stat-label">To Watch</div>
          </div>
          
          <div className="stat-card">
            <div className="stat-number">{stats.watched}</div>
            <div className="stat-label">Watched</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home