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
  const carouselRef = useRef<HTMLDivElement>(null)
  const isScrolling = useRef(false)

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
    if (carouselRef.current && overview?.recommendations?.movies?.length) {
      const carousel = carouselRef.current
      const itemWidth = 270
      const movies = overview.recommendations.movies
      // Temporarily disable smooth scroll
      carousel.style.scrollBehavior = 'auto'
      carousel.scrollLeft = itemWidth * movies.length
      // Re-enable smooth scroll
      setTimeout(() => {
        carousel.style.scrollBehavior = ''
      }, 0)
    }
  }, [overview])

  const scroll = (direction: 'left' | 'right') => {
    if (!carouselRef.current || isScrolling.current) return
    
    isScrolling.current = true
    const scrollAmount = carouselRef.current.clientWidth * 0.8
    const newPosition = direction === 'left' 
      ? carouselRef.current.scrollLeft - scrollAmount
      : carouselRef.current.scrollLeft + scrollAmount
    
    carouselRef.current.scrollTo({
      left: newPosition,
      behavior: 'smooth'
    })

    setTimeout(() => {
      isScrolling.current = false
    }, 300)
  }

  const handleScroll = () => {
    if (!carouselRef.current || !overview?.recommendations?.movies?.length || isScrolling.current) return
    
    const carousel = carouselRef.current
    const itemWidth = 270 // 250px width + 20px gap
    const movies = overview.recommendations.movies
    const setWidth = itemWidth * movies.length
    
    // Check if scrolled to beginning (before first clone set)
    if (carousel.scrollLeft < itemWidth) {
      carousel.scrollLeft = setWidth + carousel.scrollLeft
    }
    // Check if scrolled to end (after last clone set)
    else if (carousel.scrollLeft >= setWidth * 2) {
      carousel.scrollLeft = carousel.scrollLeft - setWidth
    }
  }

  if (!account || loading) {
    return null
  }

  const movies = overview?.recommendations?.movies || []
  const reason = overview?.recommendations?.reason || ''
  const stats = overview?.watchlist || { total: 0, queued: 0, watched: 0 }

  // Create infinite scroll by tripling the movie array
  const infiniteMovies = movies.length > 0 ? [...movies, ...movies, ...movies] : []
  const showCarousel = movies.length > 0

  return (
    <div className="home-container">
      <div className="home-content">
        <h1 className="welcome-message">Welcome {account.firstName}</h1>
        
        <div className="user-info">
          <div>Age: {account.age}, Rating: { account.rating}</div>
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

        {showCarousel && (
          <div className="carousel-container">
            <button 
              className="carousel-arrow carousel-arrow-left"
              onClick={() => scroll('left')}
              aria-label="Scroll left"
            >
              ‹
            </button>
            
            <div 
              className="carousel" 
              ref={carouselRef}
              onScroll={handleScroll}
            >
              {infiniteMovies.map((movie, index) => (
                <div key={`${movie.id}-${index}`} className="carousel-item">
                  <MovieTile movie={movie} />
                </div>
              ))}
            </div>

            <button 
              className="carousel-arrow carousel-arrow-right"
              onClick={() => scroll('right')}
              aria-label="Scroll right"
            >
              ›
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Home