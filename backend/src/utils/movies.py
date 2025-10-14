AGE_UNLOCK_ALL = 18
RATING_AGE_REQUIREMENTS = {
    'G': 0,
    'PG': 0,
    'PG-13': 13,
    'R': 17,
    'NC-17': AGE_UNLOCK_ALL,
}

def can_watch_rating(member_age, movie_rating):
    """Check if member age meets rating requirement"""
    if member_age >= AGE_UNLOCK_ALL: return True
    return member_age >= RATING_AGE_REQUIREMENTS.get(movie_rating, 18)

def get_allowable_ratings(age):
    return [
        rating 
        for rating, min_age in RATING_AGE_REQUIREMENTS.items()
        if age >= min_age
    ]

def get_rating(age):
    """
    Given an age, return the highest rating the user is eligible to watch.
    If the age is below all thresholds, returns the lowest rating.
    """
    # Sort ratings by minimum age requirement, descending
    sorted_ratings = sorted(RATING_AGE_REQUIREMENTS.items(), key=lambda x: x[1], reverse=True)
    for rating, min_age in sorted_ratings:
        if age >= min_age:
            return rating
    # Default to lowest rating if nothing matches
    return 'G'

def age_unlocks_ratings(prev, next):
    return get_rating(prev) != get_rating(next)

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