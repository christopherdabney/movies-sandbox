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
  const autoScrollRef = useRef<NodeJS.Timeout | null>(null)
  const hasInteractedRef = useRef(false)
  const [needsInfiniteScroll, setNeedsInfiniteScroll] = useState(false);

  //console.log(account);

  // Auto-scroll effect
  useEffect(() => {
    if (carouselRef.current && overview?.recommendations?.movies?.length && !hasInteractedRef.current && needsInfiniteScroll) {
      autoScrollRef.current = setInterval(() => {
        if (carouselRef.current) {
          carouselRef.current.scrollLeft += 1;
        }
      }, 20);
    }
    return () => {
      if (autoScrollRef.current) clearInterval(autoScrollRef.current);
    };
  }, [overview, needsInfiniteScroll]);


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
    stopAutoScroll()
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

  useEffect(() => {
    if (carouselRef.current && overview?.recommendations?.movies?.length) {
      const carousel = carouselRef.current;
      // Check if content width exceeds viewport width
      const contentWidth = overview.recommendations.movies.length * 270; // 250px width + 20px gap
      const viewportWidth = carousel.clientWidth;
      setNeedsInfiniteScroll(contentWidth > viewportWidth);
    } else {
      setNeedsInfiniteScroll(false);
    }
  }, [overview]);

  // Update the infiniteMovies calculation
  const movies = overview?.recommendations?.movies || [];
  const reason = overview?.recommendations?.reason || '';
  const stats = overview?.watchlist || { total: 0, queued: 0, watched: 0 };

  // Create infinite scroll by tripling the movie array
  // Only triple for infinite scroll, otherwise show once
  const infiniteMovies = needsInfiniteScroll && movies.length > 0
    ? [...movies, ...movies, ...movies]
    : movies;

  const showCarousel = movies.length > 0

  // Update handleScroll to only run when infinite scroll is enabled
  const handleScroll = () => {
    if (!needsInfiniteScroll || !carouselRef.current || !overview?.recommendations?.movies?.length || isScrolling.current) return;
    
    const carousel = carouselRef.current;
    const itemWidth = 270;
    const movies = overview.recommendations.movies;
    const setWidth = itemWidth * movies.length;
    
    if (carousel.scrollLeft < itemWidth) {
      carousel.scrollLeft = setWidth + carousel.scrollLeft;
    }
    else if (carousel.scrollLeft >= setWidth * 2) {
      carousel.scrollLeft = carousel.scrollLeft - setWidth;
    }
  };

  // Optionally, stop auto-scroll on manual scroll or mouse/touch
  const handleUserInteraction = () => {
    stopAutoScroll()
  }

  // Stop auto-scroll on arrow click
  const stopAutoScroll = () => {
    if (autoScrollRef.current) {
      clearInterval(autoScrollRef.current)
      autoScrollRef.current = null
    }
    hasInteractedRef.current = true
  }


  if (!account || loading) {
    return null
  }

  return (
    <div className="home-container">
      <div className="home-content">
        {account && !account.verified && (
          <div className="unverified-message">
            <span><strong>Please verify your email address</strong></span>
            <span>Check your inbox for the verification link.</span>
            <span>
              <button 
                onClick={async () => {
                  console.log('checkpoint 1');
                  try {
                    console.log(API_ENDPOINTS.MEMBER.RESEND);
                    const response = await fetch(API_ENDPOINTS.MEMBER.RESEND, {
                      method: 'POST',
                      credentials: 'include'
                    });
                    if (response.ok) {
                      alert('Verification email sent! Check your inbox.');
                    } else {
                      alert('Failed to resend email. Try again later.');
                    }
                  } catch (error) {
                    alert('Error sending email.');
                  }
                }}
                className="unverified-message"
              >
                Resend Verification Email
              </button>
            </span>
          </div>
        )}
        <h1 className="welcome-message">Welcome {account.firstName}</h1>
        <div className="user-info">
          <div>
            Age: {account.age} | 
            {account.verified ? 'verified' : 'unverified'} | 
            Unlocked Rating: { account.rating}
          </div>
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
            {needsInfiniteScroll && 
              <button 
                className="carousel-arrow carousel-arrow-left"
                onClick={() => scroll('left')}
                aria-label="Scroll left"
              >
                ‹
              </button>
            }
            
            <div 
              className="carousel" 
              ref={carouselRef}
              onScroll={handleScroll}
              onMouseDown={handleUserInteraction}
              onTouchStart={handleUserInteraction}
            >
              {infiniteMovies.map((movie, index) => (
                <div key={`${movie.id}-${index}`} className="carousel-item">
                  <MovieTile movie={movie} />
                </div>
              ))}
            </div>

            {needsInfiniteScroll && 
              <button 
                className="carousel-arrow carousel-arrow-right"
                onClick={() => scroll('right')}
                aria-label="Scroll right"
              >
                ›
              </button>
            }
          </div>
        )}
      </div>
    </div>
  )
}

export default Home