import os
import requests
import psycopg2
import time

# TMDB Configuration
TMDB_API_KEY = '3e763992a63669784fd1128de0880640'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'

# Database connection
def connect_db():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'pagine_dev'),
        user=os.getenv('DB_USER', os.getenv('USER')),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )

def search_tmdb_movie(title, year):
    """Search TMDB for movie and return poster path"""
    url = f'{TMDB_BASE_URL}/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'query': title,
        'year': year
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f'{TMDB_IMAGE_BASE}{poster_path}'
        return None
    except Exception as e:
        print(f'  Error searching TMDB: {e}')
        return None

def main():
    conn = connect_db()
    cursor = conn.cursor()
    
    # Get all movies without poster URLs
    cursor.execute("""
        SELECT id, title, release_year 
        FROM movie 
        WHERE poster_url IS NULL
        ORDER BY id
    """)
    
    movies = cursor.fetchall()
    total = len(movies)
    print(f'Found {total} movies without posters\n')
    
    success_count = 0
    fail_count = 0
    
    for idx, (movie_id, title, year) in enumerate(movies, 1):
        print(f'[{idx}/{total}] {title} ({year})... ', end='', flush=True)
        
        poster_url = search_tmdb_movie(title, year)
        
        if poster_url:
            cursor.execute(
                'UPDATE movie SET poster_url = %s WHERE id = %s',
                (poster_url, movie_id)
            )
            conn.commit()
            print(f'✓ Found')
            success_count += 1
        else:
            print('✗ Not found')
            fail_count += 1
        
        # Rate limiting: TMDB allows 40 requests/10 seconds
        time.sleep(0.3)
    
    cursor.close()
    conn.close()
    
    print(f'\n--- Summary ---')
    print(f'Success: {success_count}')
    print(f'Failed:  {fail_count}')
    print(f'Total:   {total}')

if __name__ == '__main__':
    main()