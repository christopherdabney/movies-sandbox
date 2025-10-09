import os
import random
import requests
import psycopg2
from time import sleep
from dotenv import load_dotenv

load_dotenv()

# Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

# Map choice to endpoint
category_map = {
    '1': 'popular',
    '2': 'top_rated',
    '3': 'now_playing',
    '4': 'upcoming'
}

def connect_db():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'movies_dev'),
        user=os.getenv('DB_USER', os.getenv('USER')),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )

def check_movie_exists(cursor, title, release_year):
    """Check if movie already exists in database"""
    cursor.execute(
        "SELECT id FROM movie WHERE title = %s AND release_year = %s",
        (title, release_year)
    )
    return cursor.fetchone() is not None

def insert_movie(cursor, conn, movie):
    """Insert movie into database"""
    try:
        cursor.execute("""
            INSERT INTO movie (
                title, description, director, release_year, 
                genre, rating, imdb_rating, poster_url, runtime_minutes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            movie['title'],
            movie['description'],
            movie['director'],
            movie['release_year'],
            movie['genre'],
            movie['rating'],
            movie['imdb_rating'],
            movie['poster_url'],
            movie['runtime_minutes']
        ))
        conn.commit()
        movie_id = cursor.fetchone()[0]
        return movie_id
    except Exception as e:
        conn.rollback()
        print(f"    ✗ Error inserting movie: {e}")
        return None

def fetch_movies(num_movies=10, category="popular"):
    """Fetch popular movies from TMDB API"""
    movies = []
    pages_needed = (num_movies // 20) + 1
    
    print(f"\nFetching {num_movies} movies from TMDB...")
    print("-" * 80)
    
    # Generate unique random page numbers
    random_pages = random.sample(range(1, 501), pages_needed)  # TMDB has ~500 pages

    for page in random_pages:
        url = f"{BASE_URL}/movie/{category}"
        params = {
            'api_key': TMDB_API_KEY,
            'page': page,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for movie_data in data['results']:
                if len(movies) >= num_movies:
                    break
                
                # Fetch detailed movie info
                movie_id = movie_data['id']
                detail_url = f"{BASE_URL}/movie/{movie_id}"
                detail_params = {
                    'api_key': TMDB_API_KEY,
                    'append_to_response': 'credits,release_dates'
                }
                
                detail_response = requests.get(detail_url, params=detail_params)
                detail_response.raise_for_status()
                details = detail_response.json()
                
                # Extract director
                director = None
                if 'credits' in details and 'crew' in details['credits']:
                    for person in details['credits']['crew']:
                        if person['job'] == 'Director':
                            director = person['name']
                            break
                
                # Extract US rating
                rating = None
                if 'release_dates' in details and 'results' in details['release_dates']:
                    for country in details['release_dates']['results']:
                        if country['iso_3166_1'] == 'US':
                            if country['release_dates']:
                                rating = country['release_dates'][0].get('certification')
                            break
                
                # Get primary genre
                genre = details.get('genres', [{}])[0].get('name') if details.get('genres') else None
                
                # Build movie object
                movie = {
                    'title': details.get('title'),
                    'description': details.get('overview'),
                    'director': director,
                    'release_year': int(details.get('release_date', '0000')[:4]) if details.get('release_date') else None,
                    'genre': genre,
                    'rating': rating,
                    'imdb_rating': details.get('vote_average'),
                    'poster_url': f"{IMAGE_BASE_URL}{details['poster_path']}" if details.get('poster_path') else None,
                    'runtime_minutes': details.get('runtime')
                }
                
                movies.append(movie)
                print(f"  [{len(movies)}/{num_movies}] {movie['title']} ({movie['release_year']})")
                
                # Rate limiting
                sleep(0.25)
                
            if len(movies) >= num_movies:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching movies: {e}")
            break
    
    return movies

def display_movies(movies):
    """Display movies in a readable format"""
    print("\n" + "=" * 80)
    print(f"FETCHED {len(movies)} MOVIES")
    print("=" * 80)
    
    for i, movie in enumerate(movies, 1):
        print(f"\n[{i}] {movie['title']} ({movie['release_year']})")
        print(f"    Director: {movie['director'] or 'Unknown'}")
        print(f"    Genre: {movie['genre'] or 'Unknown'}")
        print(f"    Rating: {movie['rating'] or 'NR'} | IMDB: {movie['imdb_rating']}")
        print(f"    Runtime: {movie['runtime_minutes']} min" if movie['runtime_minutes'] else "    Runtime: Unknown")
        if movie['description']:
            desc = movie['description'][:150]
            print(f"    Description: {desc}{'...' if len(movie['description']) > 150 else ''}")

def main():
    # Check API key
    if not TMDB_API_KEY:
        print("✗ ERROR: TMDB_API_KEY not found in environment!")
        print("  Add it to your .env file or set it with: export TMDB_API_KEY='your_key'")
        return
    
    # Connect to database
    try:
        conn = connect_db()
        cursor = conn.cursor()
    except Exception as e:
        print(f"✗ Error connecting to database: {e}")
        return
    
    while True:
        # Ask how many movies to fetch
        print("\n" + "=" * 80)
        try:
            num_movies = input("How many movies to fetch? (default 10): ").strip()
            num_movies = int(num_movies) if num_movies else 10
            if num_movies < 1:
                print("✗ Please enter a positive number")
                continue
        except ValueError:
            print("✗ Please enter a valid number")
            continue
        
        # Category selection
        print("\nSelect movie category:")
        print("1) Popular")
        print("2) Top Rated")
        print("3) Now Playing")
        print("4) Upcoming")

        while True:
            category_choice = input("Enter choice (1-4, default 1): ").strip()
            category_choice = category_choice if category_choice else "1"
            
            if category_choice in ['1', '2', '3', '4']:
                break
            print("Invalid choice. Please enter 1, 2, 3, or 4")
        category = category_map[category_choice]

        # Fetch movies
        movies = fetch_movies(num_movies, category)
        
        if not movies:
            print("✗ No movies fetched")
            break

        # Display results
        display_movies(movies)
        
        # Ask to insert
        print("\n" + "=" * 80)
        insert = input("Insert these movies into the database? (yes/no): ").strip().lower()
        
        if insert in ['yes', 'y']:
            print("\nInserting movies into database...")
            print("-" * 80)
            
            inserted_count = 0
            skipped_count = 0
            
            for i, movie in enumerate(movies, 1):
                # Check if movie exists
                if check_movie_exists(cursor, movie['title'], movie['release_year']):
                    print(f"  [{i}/{len(movies)}] {movie['title']} ({movie['release_year']}) - Already exists, skipping")
                    skipped_count += 1
                    continue
                
                # Insert movie
                movie_id = insert_movie(cursor, conn, movie)
                if movie_id:
                    print(f"  [{i}/{len(movies)}] {movie['title']} ({movie['release_year']}) - ✓ Inserted (ID: {movie_id})")
                    inserted_count += 1
                else:
                    skipped_count += 1
            
            print("\n" + "-" * 80)
            print(f"✓ Inserted: {inserted_count} | Skipped: {skipped_count} | Total: {len(movies)}")
            
            # Ask to continue
            print("\n" + "=" * 80)
            again = input("Fetch more movies? (yes/no): ").strip().lower()
            if again not in ['yes', 'y']:
                break
        else:
            print("\n✓ Exiting without inserting")
            break
    
    cursor.close()
    conn.close()
    print("\n✓ Complete!")

if __name__ == '__main__':
    main()