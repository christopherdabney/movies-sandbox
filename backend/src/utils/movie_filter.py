"""
Utility functions for filtering movies based on user queries
"""
from models import Movie
from sqlalchemy import and_, or_

def extract_filters(user_message):
    """
    Extract genre and decade filters from user message
    
    Returns:
        dict with 'genres' and 'decades' keys
    """
    message_lower = user_message.lower()
    
    # Genre keywords
    genre_map = {
        'action': 'Action',
        'comedy': 'Comedy',
        'drama': 'Drama',
        'horror': 'Horror',
        'thriller': 'Thriller',
        'sci-fi': 'Sci-Fi',
        'science fiction': 'Sci-Fi',
        'romance': 'Romance',
        'romantic': 'Romance',
        'animation': 'Animation',
        'animated': 'Animation',
        'adventure': 'Adventure',
        'fantasy': 'Fantasy',
        'crime': 'Crime',
        'mystery': 'Mystery',
        'western': 'Western',
        'musical': 'Musical',
    }
    
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
    
    # Extract genres
    detected_genres = []
    for keyword, genre in genre_map.items():
        if keyword in message_lower:
            detected_genres.append(genre)
    
    # Extract decades
    detected_decades = []
    for keyword, (start, end) in decade_keywords.items():
        if keyword in message_lower:
            detected_decades.append((start, end))
    
    return {
        'genres': list(set(detected_genres)),  # Remove duplicates
        'decades': detected_decades
    }


def get_filtered_movies(filters, limit=100):
    """
    Get movies filtered by genre and/or decade
    
    Args:
        filters: dict with 'genres' and 'decades' keys
        limit: maximum number of movies to return
    
    Returns:
        List of Movie objects
    """
    query = Movie.query
    
    conditions = []
    
    # Add genre filters
    if filters['genres']:
        genre_conditions = [Movie.genre == g for g in filters['genres']]
        conditions.append(or_(*genre_conditions))
    
    # Add decade filters
    if filters['decades']:
        decade_conditions = []
        for start, end in filters['decades']:
            decade_conditions.append(
                and_(Movie.release_year >= start, Movie.release_year <= end)
            )
        conditions.append(or_(*decade_conditions))
    
    # Apply all conditions
    if conditions:
        query = query.filter(and_(*conditions))
    
    return query.limit(limit).all()