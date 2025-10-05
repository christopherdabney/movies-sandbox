from database import db

class Movie(db.Model):
    __tablename__ = 'movie'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100))
    release_year = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    description = db.Column(db.Text)
    runtime_minutes = db.Column(db.Integer)
    rating = db.Column(db.String(10))  # PG, PG-13, R, etc.
    imdb_rating = db.Column(db.Numeric(3,1))
    poster_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'director': self.director,
            'release_year': self.release_year,
            'genre': self.genre,
            'description': self.description,
            'runtime_minutes': self.runtime_minutes,
            'rating': self.rating,
            'imdb_rating': float(self.imdb_rating) if self.imdb_rating else None,
            'poster_url': self.poster_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Movie {self.title} ({self.release_year})>'

    @staticmethod
    def extract_filters(user_message):
        """
        Extract decade filters from user message
        
        Returns:
            dict with 'decades' key
        """
        message_lower = user_message.lower()
        
        # Decade keywords
        decade_keywords = {
            '1920s': (1920, 1929),
            '1930s': (1930, 1939),
            '1940s': (1940, 1949),
            '1950s': (1950, 1959),
            '1960s': (1960, 1969),
            '1970s': (1970, 1979),
            '1980s': (1980, 1989),
            '1990s': (1990, 1999),
            '2000s': (2000, 2009),
            '90s': (1990, 1999),
            '80s': (1980, 1989),
            '70s': (1970, 1979),
            '60s': (1960, 1969),
        }
        
        # Extract decades
        detected_decades = []
        for keyword, (start, end) in decade_keywords.items():
            if keyword in message_lower:
                detected_decades.append((start, end))
        
        return {
            'decades': detected_decades
        }
    
    @staticmethod
    def find_by_filters(filters, limit=100):
        """
        Get movies filtered by decade
        
        Args:
            filters: dict with 'decades' key
            limit: maximum number of movies to return
        
        Returns:
            List of Movie objects
        """
        query = Movie.query
        
        # Add decade filters
        if filters['decades']:
            decade_conditions = []
            for start, end in filters['decades']:
                decade_conditions.append(
                    and_(Movie.release_year >= start, Movie.release_year <= end)
                )
            query = query.filter(or_(*decade_conditions))
        
        return query.limit(limit).all()