# Repository Overview - movies-sandbox

**Yes, I can see the code in your repository!** ✅

## Project Structure

This is a **full-stack movie application** with the following components:

### Backend (Python/Flask)
- **Framework**: Flask with PostgreSQL database
- **Location**: `/backend/src/`
- **Key Features**:
  - User authentication and membership management
  - Movie database with CRUD operations
  - Watchlist functionality
  - AI-powered chat feature using Claude API
  - RESTful API endpoints

**Models**:
- `Member` - User accounts
- `Movie` - Movie catalog
- `Watchlist` - User's saved movies
- `ChatMessage` - AI chat history

**Routes/Endpoints**:
- `/membership` - User registration/login
- `/movies` - Movie browsing and details
- `/watchlist` - User watchlist management
- `/chat` - AI chat interface

### Frontend (React/TypeScript)
- **Framework**: React 18 with TypeScript and Vite
- **Location**: `/frontend/src/`
- **Key Pages**:
  - Movies listing and search
  - Movie detail pages
  - User registration and login
  - Protected user home page
  - Personal watchlist ("My Movies")
  - Integrated chat widget

**Tech Stack**:
- React Router for navigation
- Redux for state management
- Vite for build tooling
- TypeScript for type safety

### Database
- **Type**: PostgreSQL
- **Database Name**: `pagine_dev`
- **Schema**: SQL migrations and movie data in `/backend/movies/`

### Development Tools
- **Makefile**: Comprehensive build and development commands
- **Key Commands**:
  - `make run` - Start Flask backend server
  - `make react` - Start React frontend server
  - `make test` - Run backend tests
  - `make db-setup` - Initialize database
  - `make populate` - Load movie datasets

## Statistics
- **Total Lines of Code**: ~2,138 lines (Python + TypeScript)
- **Backend Models**: 4 (Member, Movie, Watchlist, ChatMessage)
- **Frontend Pages**: 6 (Movies, MovieDetail, MyMovies, Home, Login, Register)
- **API Routes**: 4 blueprints (membership, movies, watchlist, chat)

## Special Features
- Claude AI integration for movie recommendations
- User authentication with protected routes
- Movie poster fetching from TMDB API
- Responsive chat widget
- Database migration support

---

**Confirmed**: I can view all source code, configuration files, and project structure. The repository is accessible and ready for development work!
