import { useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { accountRecord } from '../store/accountSlice'
import type { AppDispatch, RootState } from '../store/store'
import { API_ENDPOINTS } from '../constants/api'
import MovieTile from '../components/MovieTile'
import type { Movie } from '../types'
import './../styles/Home.css'

interface OverviewResponse {
  watchlist: {
    total: number;
    queued: number;
    watched: number;
  };
  recommendations: {
    movies: Movie[];
    reason: string;
  };
}

function Home() {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { account } = useSelector((state: RootState) => state.account)
  const [overview, setOverview] = useState<OverviewResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [scrollPosition, setScrollPosition] = useState(0)
  const [showLeftArrow, setShowLeftArrow] = useState(false)
  const [showRightArrow, setShowRightArrow] = useState(false)
  const carouselRef = useRef<HTMLDivElement>(null)

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
    const fetchOverview = async () => {
      try {
        setLoading(true)
        const response = await fetch(API_ENDPOINTS.WATCHLIST.OVERVIEW, {
          credentials: 'include',
        })
        const data: OverviewResponse = await response.json()
        setOverview(data)
      } catch (error) {
        console.error('Error fetching overview:', error)
      } finally {
        setLoading(false)
      }
    }
    
    if (account) {
      fetchOverview()
    }
  }, [account])

  useEffect(() => {
    updateArrowVisibility()
  }, [overview, scrollPosition])

  const updateArrowVisibility = () => {
    if (!carouselRef.current) return
    
    const { scrollLeft, scrollWidth, clientWidth } = carouselRef.current
    setShowLeftArrow(scrollLeft > 0)
    setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10)
  }

  const scroll = (direction: 'left' | 'right') => {
    if (!carouselRef.current) return
    
    const scrollAmount = carouselRef.current.clientWidth * 0.8
    const newPosition = direction === 'left' 
      ? carouselRef.current.scrollLeft - scrollAmount
      : carouselRef.current.scrollLeft + scrollAmount
    
    carouselRef.current.scrollTo({
      left: newPosition,
      behavior: 'smooth'
    })
  }

  const handleScroll = () => {
    if (carouselRef.current) {
      setScrollPosition(carouselRef.current.scrollLeft)
    }
  }

  if (!account || loading) {
    return null
  }

  const movies = overview?.recommendations?.movies || []
  const reason = overview?.recommendations?.reason || ''
  const stats = overview?.watchlist || { total: 0, queued: 0, watched: 0 }

  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="welcome-message">Welcome {account.firstName}</h1>
        
        <div className="user-info">
          <div>Age: {account.age}, Rating: PG-13</div>
        </div>

        <table className="stats-table">
          <tbody>
            <tr>
              <td>Watched films:</td>
              <td>{stats.watched}</td>
            </tr>
            <tr>
              <td>Queue films:</td>
              <td>{stats.queued}</td>
            </tr>
            <tr>
              <td>Total films:</td>
              <td>{stats.total}</td>
            </tr>
          </tbody>
        </table>

        {reason && <div className="recommendation-message">{reason}</div>}

        {movies.length > 0 && (
          <div className="carousel-container">
            {showLeftArrow && (
              <button 
                className="carousel-arrow carousel-arrow-left"
                onClick={() => scroll('left')}
                aria-label="Scroll left"
              >
                ‹
              </button>
            )}
            
            <div 
              className="carousel" 
              ref={carouselRef}
              onScroll={handleScroll}
            >
              {movies.map((movie) => (
                <div key={movie.id} className="carousel-item">
                  <MovieTile movie={movie} />
                </div>
              ))}
            </div>

            {showRightArrow && (
              <button 
                className="carousel-arrow carousel-arrow-right"
                onClick={() => scroll('right')}
                aria-label="Scroll right"
              >
                ›
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Home