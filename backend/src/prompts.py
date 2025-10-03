"""
Chat prompts for the movie recommendation assistant
"""

SYSTEM_PROMPT = """You are a helpful movie recommendation assistant. 
Keep responses SHORT - 2-3 sentences max.
Only recommend movies from the provided database.
Personalize based on the user's watchlist when relevant."""


def build_movie_context(watchlist_movies, available_movies):
    """
    Build context string with user's watchlist and available movies
    
    Args:
        watchlist_movies: List of strings describing watchlist items
        available_movies: List of strings describing available movies
    
    Returns:
        Formatted context string for Claude
    """
    watchlist_section = "\n".join(watchlist_movies) if watchlist_movies else "Empty - user hasn't added any movies yet"
    available_section = "\n".join(available_movies)
    
    return f"""You are a movie recommendation assistant for this user.

USER'S WATCHLIST ({len(watchlist_movies)} movies):
{watchlist_section}

AVAILABLE MOVIES IN DATABASE (showing {len(available_movies)} of our collection):
{available_section}

Only recommend movies from the available list above. Reference the user's watchlist when making personalized suggestions."""